import re

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models


REGEX_INVALID_USERNAME = re.compile(settings.INVALID_USERNAME_PATTERN)
MIN_COOCKING_TIME = 1
MIN_INGREDIENT_AMOUNT = 1


class Ingredient(models.Model):
    name = models.CharField('Название', max_length=128)
    measurement_unit = models.CharField(
        'Единица измерения',
        max_length=64,
    )

    class Meta:
        verbose_name = 'Продукт'
        verbose_name_plural = 'Продукты'
        ordering = ('name',)
        constraints = (
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='unique_ingredient_entry',
            ),
        )

    def __str__(self):
        return f'{self.name} ({self.measurement_unit})'


class Tag(models.Model):
    name = models.CharField('Название', max_length=32, unique=True)
    slug = models.SlugField('Слаг', max_length=32, unique=True)

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Recipe(models.Model):
    name = models.CharField('Название', max_length=256)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='Автор',
    )
    tags = models.ManyToManyField(Tag, verbose_name='Теги')
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        verbose_name='Продукты',
    )
    image = models.ImageField('Фото', upload_to='recipes/images/')
    text = models.TextField('Текст')
    cooking_time = models.PositiveIntegerField(
        'Время (мин)', validators=(MinValueValidator(MIN_COOCKING_TIME),)
    )
    created_at = models.DateTimeField('Создан', auto_now_add=True)

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-created_at',)
        default_related_name = 'recipes'

    def __str__(self):
        return f'{self.name[:20]} — {self.author}'


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Продукт',
    )
    amount = models.PositiveIntegerField(
        'Количество',
        validators=(MinValueValidator(MIN_INGREDIENT_AMOUNT),),
    )

    class Meta:
        verbose_name = 'Продукт в рецепте'
        verbose_name_plural = 'Продукты в рецепте'
        constraints = (
            models.UniqueConstraint(
                fields=('recipe', 'ingredient'),
                name='unique_recipe_ingredient',
            ),
        )
        default_related_name = 'recipe_ingredients'

    def __str__(self):
        return (
            f'{self.ingredient.name} — {self.amount} '
            f'{self.ingredient.measurement_unit} (в {self.recipe.name})'
        )


def username_validator(username: str):
    """Валидирует никнейм.
    Выбрасывает ошибку со списком некорректных символов."""
    invalid_chars = REGEX_INVALID_USERNAME.findall(username)
    if invalid_chars:
        raise ValidationError(
            'Некорректные символы в никнейме: {}'.format(
                ''.join(invalid_chars)
            )
        )


class User(AbstractUser):
    username = models.CharField(
        'Никнейм',
        max_length=150,
        unique=True,
        validators=(username_validator,),
    )
    email = models.EmailField(
        'Адрес эл. почты',
        max_length=254,
        unique=True,
    )
    first_name = models.CharField('Имя', max_length=150)
    last_name = models.CharField('Фамилия', max_length=150)
    avatar = models.ImageField(
        'Аватар',
        upload_to='users/avatars/',
        blank=True,
        null=True,
    )
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'first_name', 'last_name')

    def __str__(self):
        return f'{self.username}'


class Subscription(models.Model):
    from_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='От пользователя',
        related_name='from_user_subscriptions',
    )
    to_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='К пользователю',
        related_name='to_user_subscriptions',
    )

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=('from_user', 'to_user'),
                name='unique_subscription',
            ),
        )
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self):
        return f'{self.from_user} → {self.to_user}'


class UserRecipeRelation(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
    )

    class Meta:
        abstract = True
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_%(class)s_user_recipe',
            ),
        )
        default_related_name = '%(class)ss'

    def __str__(self) -> str:
        return f"Рецепт '{self.recipe.name[:10]}' сохранён у {self.user}"


class Favorite(UserRecipeRelation):
    class Meta(UserRecipeRelation.Meta):
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'


class ShoppingCartItem(UserRecipeRelation):
    class Meta(UserRecipeRelation.Meta):
        verbose_name = 'Рецепт в корзине'
        verbose_name_plural = 'Рецепты в корзине'
