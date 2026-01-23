from django.contrib.auth.models import AbstractUser
from django.db import models

from recipes.models import Recipe


class User(AbstractUser):
    ROLE_CHOICES = (
        ('user', 'User'),
        ('admin', 'Admin'),
    )

    email = models.EmailField(
        unique=True,
        verbose_name='Адрес эл. почты',
        max_length=254,
    )
    avatar = models.ImageField(
        'Аватар',
        upload_to='users/avatars/',
        blank=True,
        null=True,
    )
    role = models.CharField(
        'Роль',
        max_length=10,
        choices=ROLE_CHOICES,
        default='user',
    )

    def __str__(self):
        return self.username

    def is_admin(self) -> bool:
        return self.role == 'admin' or self.is_staff


class Subscription(models.Model):
    from_user = models.ForeignKey(
        User,
        related_name='subscriptions',
        on_delete=models.CASCADE,
        verbose_name='От пользователя',
    )
    to_user = models.ForeignKey(
        User,
        related_name='subscribers',
        on_delete=models.CASCADE,
        verbose_name='К пользователю',
    )
    created_at = models.DateTimeField(
        'Дата подписки',
        auto_now_add=True,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['from_user', 'to_user'],
                name='unique_subscription',
            ),
        ]
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self):
        return f'{self.from_user} → {self.to_user}'


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        related_name='favorites',
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        related_name='favorited_by',
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
    )
    created_at = models.DateTimeField('Добавлено', auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_favorite',
            ),
        ]
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'

    def __str__(self) -> str:
        return f'{self.recipe.name[:10]} в избранном у {self.user}'


class ShoppingCartItem(models.Model):
    user = models.ForeignKey(
        User,
        related_name='shopping_cart',
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        related_name='in_shopping_carts',
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
    )
    added_at = models.DateTimeField(
        'Добавлено',
        auto_now_add=True,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_shopping_cart_item',
            ),
        ]
        verbose_name = 'Объект в корзине'
        verbose_name_plural = 'Объекты в корзине'

    def __str__(self) -> str:
        return f'{self.recipe.name[:10]} в корзине у {self.user}'
