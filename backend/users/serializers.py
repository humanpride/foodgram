from django.contrib.auth import get_user_model
from rest_framework import serializers

from recipes.models import Recipe
from recipes.serializers import RecipeListSerializer

User = get_user_model()


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'password',
        )

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()
    avatar = serializers.ImageField(read_only=True)

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'avatar',
            'is_subscribed',
        )

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        user = getattr(request, 'user', None)
        if not user or not user.is_authenticated:
            return False
        return user.subscription_set.filter(to_user=obj).exists()


class UserWithRecipesSerializer(UserSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ('recipes', 'recipes_count')

    def get_recipes(self, obj):
        # recipes_limit is handled in the view
        # by passing in context['recipes_limit'] OR via request query param
        limit = self.context.get('recipes_limit')
        qs = Recipe.objects.filter(author=obj).order_by('-id')
        if limit:
            qs = qs[: int(limit)]
        serializer = RecipeListSerializer(qs, many=True, context=self.context)
        return serializer.data

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj).count()


class SetAvatarSerializer(serializers.Serializer):
    avatar = serializers.CharField()  # base64 string

    def validate_avatar(self, value):
        # reuse Base64ImageField decode:
        # we can instantiate it and call to_internal_value
        from core.fields import Base64ImageField

        field = Base64ImageField()
        file = field.to_internal_value(value)  # raise ValidationError if wrong
        return file

    def save(self, user):
        file = self.validated_data['avatar']
        user.avatar.save(file.name, file, save=True)
        return user
