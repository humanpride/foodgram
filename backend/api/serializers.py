from collections import Counter

from django.db import transaction
from djoser import serializers as djoser_serializers
from rest_framework import serializers as django_serializers

from api.fields import Base64ImageField
from recipes.models import (
    MIN_COOCKING_TIME,
    MIN_INGREDIENT_AMOUNT,
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCartItem,
    Tag,
)


class IngredientSerializer(django_serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientInRecipeWriteSerializer(django_serializers.Serializer):
    id = django_serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all()
    )
    amount = django_serializers.IntegerField(min_value=MIN_INGREDIENT_AMOUNT)


class IngredientInRecipeReadSerializer(django_serializers.ModelSerializer):
    id = django_serializers.IntegerField(source='ingredient.id')
    name = django_serializers.CharField(source='ingredient.name')
    measurement_unit = django_serializers.CharField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')
        read_only_fields = fields


class TagSerializer(django_serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')


class UserSerializer(djoser_serializers.UserSerializer):
    is_subscribed = django_serializers.SerializerMethodField()

    class Meta(djoser_serializers.UserSerializer.Meta):
        fields = (
            *djoser_serializers.UserSerializer.Meta.fields,
            'is_subscribed',
            'avatar',
        )
        read_only_fields = fields

    def get_is_subscribed(self, target_user):
        current_user = self.context['request'].user
        return (
            current_user.is_authenticated
            and current_user.from_user_subscriptions.filter(
                to_user=target_user
            ).exists()
        )


class UserWithRecipesSerializer(UserSerializer):
    recipes = django_serializers.SerializerMethodField()
    recipes_count = django_serializers.IntegerField(source='recipes.count')

    class Meta(UserSerializer.Meta):
        fields = (*UserSerializer.Meta.fields, 'recipes', 'recipes_count')
        read_only_fields = fields

    def get_recipes(self, user):
        limit = self.context['request'].query_params.get('recipes_limit')
        recipes = user.recipes.all()
        if limit:
            recipes = recipes[: int(limit)]
        return RecipeShortSerializer(
            recipes, many=True, context=self.context
        ).data


class RecipeReadSerializer(django_serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    author = UserSerializer()
    ingredients = IngredientInRecipeReadSerializer(
        many=True, source='recipe_ingredients'
    )
    is_favorited = django_serializers.SerializerMethodField()
    is_in_shopping_cart = django_serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )
        read_only_fields = fields

    def _is_added(self, recipe, relation_model):
        user = self.context['request'].user
        return (
            user.is_authenticated
            and relation_model.objects.filter(
                user=user, recipe=recipe
            ).exists()
        )

    def get_is_favorited(self, recipe):
        return self._is_added(recipe, Favorite)

    def get_is_in_shopping_cart(self, recipe):
        return self._is_added(recipe, ShoppingCartItem)


class RecipeCreateUpdateSerializer(django_serializers.ModelSerializer):
    cooking_time = django_serializers.IntegerField(min_value=MIN_COOCKING_TIME)
    image = Base64ImageField()
    ingredients = IngredientInRecipeWriteSerializer(
        many=True,
        write_only=True,
        required=True,
    )
    tags = django_serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
        required=True,
    )

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'text',
            'cooking_time',
            'image',
            'ingredients',
            'tags',
        )

    def _validate_duplicates(
        self,
        values,
        field_name,
        id_getter,
        error_message: str,
    ):
        ids = [id_getter(value) for value in values]
        duplicates = [
            value_id for value_id, count in Counter(ids).items() if count > 1
        ]

        if not duplicates:
            return

        raise django_serializers.ValidationError(
            error_message.format(sorted(duplicates))
        )

    def validate_tags(self, tags):
        self._validate_duplicates(
            values=tags,
            field_name='tags',
            id_getter=lambda tag: tag.id,
            error_message='Теги с id {} повторяются.',
        )
        return tags

    def validate_ingredients(self, ingredients):
        if not ingredients:
            raise django_serializers.ValidationError(
                {'ingredients': ['Укажите хотя бы 1 продукт.']}
            )

        self._validate_duplicates(
            values=ingredients,
            field_name='ingredients',
            id_getter=lambda item: item['id'].id,
            error_message='Продукты с id {} повторяются.',
        )
        return ingredients

    def validate(self, attrs):
        """
        Дополнительная валидация: при `partial=True` (PATCH).

        Требуем, чтобы оба поля `ingredients` и `tags` присутствовали
        в исходных данных запроса.
        """
        if self.partial:
            missing = {}
            if 'ingredients' not in self.initial_data:
                missing['ingredients'] = ['Это поле обязательно.']
            if 'tags' not in self.initial_data:
                missing['tags'] = ['Это поле обязательно.']
            if missing:
                raise django_serializers.ValidationError(missing)

        return attrs

    def _create_recipe_ingredient_rows(self, recipe, ingredients_data):
        RecipeIngredient.objects.bulk_create(
            RecipeIngredient(
                recipe=recipe,
                ingredient=item['id'],
                amount=item['amount'],
            )
            for item in ingredients_data
        )

    @transaction.atomic
    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')

        recipe = super().create(validated_data)
        recipe.tags.set(tags)
        self._create_recipe_ingredient_rows(recipe, ingredients_data)

        return recipe

    @transaction.atomic
    def update(self, recipe, validated_data):
        ingredients_data = validated_data.pop('ingredients', None)
        tags = validated_data.pop('tags', None)

        recipe.tags.set(tags)

        RecipeIngredient.objects.filter(recipe=recipe).delete()
        self._create_recipe_ingredient_rows(recipe, ingredients_data)

        return super().update(recipe, validated_data)

    def to_representation(self, instance):
        return RecipeReadSerializer(instance, context=self.context).data


class RecipeShortSerializer(RecipeReadSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = fields


class SetAvatarSerializer(django_serializers.Serializer):
    avatar = django_serializers.CharField()

    def validate_avatar(self, base64_string):
        return Base64ImageField().to_internal_value(base64_string)

    def save(self, user):
        file = self.validated_data['avatar']
        user.avatar.save(file.name, file, save=True)
        return user
