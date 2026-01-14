from typing import Dict, List

from django.db import transaction
from rest_framework import serializers

from core.fields import Base64ImageField
from ingredients.models import Ingredient
from recipes.models import Recipe, RecipeIngredient
from tags.models import Tag
from users.models import Favorite, ShoppingCartItem
from users.serializers import UserSerializer


class IngredientInRecipeWriteSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    amount = serializers.IntegerField(min_value=1)

    def validate_ingredient(self, id):
        if not Ingredient.objects.filter(id=id).exists():
            raise serializers.ValidationError(
                'Ингредиент с таким id не найден.'
            )
        return id


class IngredientInRecipeReadSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.CharField(source='ingredient.name')
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit'
    )
    amount = serializers.IntegerField()

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeDetailSerializer(serializers.ModelSerializer):
    tags = serializers.SerializerMethodField()
    author = UserSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

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

    def get_tags(self, obj):
        return [
            {'id': t.id, 'name': t.name, 'slug': t.slug}
            for t in obj.tags.all()
        ]

    def get_ingredients(self, recipe):
        # recipe_ingredients = RecipeIngredient.objects.filter(
        #     recipe=obj
        # ).select_related('ingredient')
        return IngredientInRecipeReadSerializer(
            RecipeIngredient.objects.filter(recipe=recipe).select_related(
                'ingredient'
            ),
            many=True,
        ).data

    def _user(self):
        return self.context['request'].user

    def get_is_favorited(self, obj):
        user = self._user()
        if not user or not user.is_authenticated:
            return False
        return Favorite.objects.filter(user=user, recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self._user()
        if not user or not user.is_authenticated:
            return False
        return ShoppingCartItem.objects.filter(user=user, recipe=obj).exists()


class RecipeCreateUpdateBaseSerializer(serializers.ModelSerializer):
    image = Base64ImageField()
    ingredients = IngredientInRecipeWriteSerializer(many=True, write_only=True)
    tags = serializers.ListField(
        child=serializers.IntegerField(), allow_empty=False
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

    def validate_tags(self, value):
        input_tags = set(value)
        tags_qs = Tag.objects.filter(id__in=input_tags)
        if tags_qs.count() != len(input_tags):
            raise serializers.ValidationError(
                'Один или более тегов не найдены.'
            )
        return tuple(input_tags)

    def validate_ingredients(self, ingredients: List[Dict[str, int]]):
        if not ingredients:
            raise serializers.ValidationError('Укажите хотя бы 1 ингредиент.')
        ids = [ingredient['id'] for ingredient in ingredients]
        ingr_qs = Ingredient.objects.filter(id__in=ids)
        if ingr_qs.count() != len(ids):
            raise serializers.ValidationError(
                'Один или более ингредиентов не найдены.'
            )
        return ingredients

    def _create_recipe_ingredient_rows(self, recipe, ingredients_data):
        rows = []
        for item in ingredients_data:
            ing = Ingredient.objects.get(id=item['id'])
            rows.append(
                RecipeIngredient(
                    recipe=recipe, ingredient=ing, amount=item['amount']
                )
            )
        RecipeIngredient.objects.bulk_create(rows)

    @transaction.atomic
    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        tags_ids = validated_data.pop('tags')
        author = self.context['request'].user
        validated_data['author'] = author
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(Tag.objects.filter(id__in=tags_ids))
        self._create_recipe_ingredient_rows(recipe, ingredients_data)
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('ingredients', None)
        tags_ids = validated_data.pop('tags', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if tags_ids is not None:
            instance.tags.set(Tag.objects.filter(id__in=tags_ids))

        if ingredients_data is not None:
            RecipeIngredient.objects.filter(recipe=instance).delete()
            self._create_recipe_ingredient_rows(instance, ingredients_data)

        return instance

    def to_representation(self, instance):
        return RecipeDetailSerializer(instance, context=self.context).data


class RecipeCreateSerializer(RecipeCreateUpdateBaseSerializer):
    class Meta(RecipeCreateUpdateBaseSerializer.Meta):
        pass


class RecipeUpdateSerializer(RecipeCreateUpdateBaseSerializer):
    class Meta(RecipeCreateUpdateBaseSerializer.Meta):
        read_only_fields = ('id',)


class RecipeListSerializer(RecipeDetailSerializer):
    class Meta(RecipeDetailSerializer.Meta):
        pass
