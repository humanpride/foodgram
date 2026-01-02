from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import Favorite, ShoppingCartItem, Subscription, User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    """
    Кастомная админка пользователя
    """

    list_display = (
        'id',
        'username',
        'email',
        'role',
        'is_active',
        'is_staff',
    )

    search_fields = ('email', 'username')
    list_filter = ('role', 'is_active')

    ordering = ('id',)

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (
            'Персональная информация',
            {'fields': ('email', 'first_name', 'last_name', 'avatar')},
        ),
        (
            'Права доступа',
            {'fields': ('role', 'is_active', 'is_staff', 'is_superuser')},
        ),
        ('Даты', {'fields': ('last_login', 'date_joined')}),
    )


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('id', 'from_user', 'to_user')
    search_fields = ('from_user__username', 'to_user__username')


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe')
    search_fields = ('user__username', 'recipe__name')


@admin.register(ShoppingCartItem)
class ShoppingCartItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe')
    search_fields = ('user__username', 'recipe__name')
