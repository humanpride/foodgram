from django.contrib.auth import get_user_model
from rest_framework import serializers

from recipes.models import Recipe


User = get_user_model()


class UserCreateSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150)

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password',
        )
        read_only_fields = ('id',)
        extra_kwargs = {'password': {'write_only': True}}

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
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'avatar',
        )

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        if not user or not user.is_authenticated:
            return False
        return user.subscriptions.filter(to_user=obj).exists()


class UserWithRecipesSerializer(UserSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ('recipes', 'recipes_count')

    def get_recipes(self, obj):
        from recipes.serializers import RecipeListSerializer

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
        from core.fields import Base64ImageField

        field = Base64ImageField()
        file = field.to_internal_value(value)
        return file

    def save(self, user):
        file = self.validated_data['avatar']
        user.avatar.save(file.name, file, save=True)
        return user


class SetPasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)

    def validate_current_password(self, value):
        user = self.context['request'].user
        if not user or not user.check_password(value):
            raise serializers.ValidationError('Текущий пароль неверный.')
        return value

    def save(self, **kwargs):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user
