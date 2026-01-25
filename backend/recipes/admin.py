from typing import Any

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.db.models import Count, QuerySet
from django.http import HttpRequest
from django.utils.html import format_html

from recipes.models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCartItem,
    Subscription,
    Tag,
    User,
)


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    fk_name = 'recipe'
    extra = 1


class CookingTimeHistogramFilter(admin.SimpleListFilter):
    title = 'Время приготовления'
    parameter_name = 'cooking_time_bin'

    def _get_thresholds(self, recipes: QuerySet):
        """
        Возвращает (M, N) — пороги для 3 бинов
        """
        values = recipes.order_by('cooking_time').values_list(
            'cooking_time', flat=True
        )

        if not values:
            return None, None

        total = len(values)
        fast_idx = total // 3
        long_idx = (total * 2) // 3

        return values[fast_idx], values[long_idx]

    def lookups(self, request, model_admin):
        recipes = model_admin.get_queryset(request)

        fast, long = self._get_thresholds(recipes)

        if (fast, long) == (None, None):
            return

        fast_count = recipes.filter(cooking_time__lt=fast).count()
        mid_count = recipes.filter(cooking_time__lt=long).count()
        long_count = recipes.filter(cooking_time__gte=long).count()

        return (
            ('fast', f'быстрее {fast} мин ({fast_count})'),
            ('mid', f'быстрее {long} мин ({mid_count})'),
            ('long', f'долго ({long_count})'),
        )

    def queryset(self, request, recipes):
        fast, long = self._get_thresholds(recipes)
        if (fast, long) == (None, None):
            return recipes

        choice = self.value()

        match choice:
            case 'fast':
                return recipes.filter(cooking_time__lt=fast)
            case 'mid':
                return recipes.filter(cooking_time__lt=long)
            case 'long':
                return recipes.filter(cooking_time__gte=long)
            case _:
                return recipes


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'cooking_time',
        'author',
        'favorites_count',
        'ingredients_html',
        'tags_html',
        'image_html',
    )

    search_fields = (
        'name',
        'author__username',
        'author__first_name',
        'author__last_name',
        'tags__name',
        'ingredients__name',
    )
    list_filter = (CookingTimeHistogramFilter, 'author', 'tags')
    inlines = (RecipeIngredientInline,)

    def get_queryset(self, request):
        recipes = super().get_queryset(request)
        return recipes.annotate(
            _favorites_count=Count('favorites', distinct=True)
        )

    @admin.display(description='В избранном')
    def favorites_count(self, recipe):
        return recipe._favorites_count

    @admin.display(description='Продукты')
    def ingredients_html(self, recipe):
        ingredients = recipe.ingredients.all()
        return format_html(
            '<br>'.join(
                f'{ingredient.name} ({ingredient.measurement_unit})'
                for ingredient in ingredients
            )
        )

    @admin.display(description='Теги')
    def tags_html(self, recipe):
        return ', '.join(tag.name for tag in recipe.tags.all())

    @admin.display(description='Фото')
    def image_html(self, recipe):
        return format_html(
            (
                '<img src="{}" width="80" height="60" '
                'style="object-fit: cover;" />'
            ),
            recipe.image.url,
        )


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'recipe', 'ingredient', 'amount')
    search_fields = ('recipe__name', 'ingredient__name')


class InRecipesFilter(admin.SimpleListFilter):
    title = 'Есть в рецептах'
    parameter_name = 'in_recipes'

    def lookups(self, request, model_admin):
        return (
            ('yes', 'Да'),
            ('no', 'Нет'),
        )

    def queryset(self, request, ingredients: QuerySet):
        choice = self.value()

        match choice:
            case 'yes':
                return ingredients.filter(_recipes_count__gt=0)
            case 'no':
                return ingredients.filter(_recipes_count=0)
            case _:
                return ingredients


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'measurement_unit', 'recipes_count')
    search_fields = ('name', 'measurement_unit')
    ordering = ('name',)
    list_filter = (InRecipesFilter, 'measurement_unit')

    def get_queryset(self, request):
        ingredients = super().get_queryset(request)
        return ingredients.annotate(
            _recipes_count=Count('recipes', distinct=True)
        )

    @admin.display(description='Число рецептов')
    def recipes_count(self, ingredient):
        return ingredient._recipes_count


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug', 'recipes_count')
    search_fields = ('name', 'slug')

    def get_queryset(self, request):
        tags = super().get_queryset(request)
        return tags.annotate(_recipes_count=Count('recipes', distinct=True))

    @admin.display(description='Число рецептов')
    def recipes_count(self, tag):
        return tag._recipes_count


class HasRecipesFilter(admin.SimpleListFilter):
    title = 'Есть рецепты'
    parameter_name = 'has_recipes'

    def lookups(self, request, model_admin):
        return (
            ('yes', 'Да'),
            ('no', 'Нет'),
        )

    def queryset(self, request, users: QuerySet):
        choice = self.value()

        match choice:
            case 'yes':
                return users.filter(_recipes_count__gt=0)
            case 'no':
                return users.filter(_recipes_count=0)
            case _:
                return users


class HasSubscriptionsFilter(admin.SimpleListFilter):
    title = 'Есть подписки'
    parameter_name = 'has_subscriptions'

    def lookups(self, request, model_admin):
        return (
            ('yes', 'Да'),
            ('no', 'Нет'),
        )

    def queryset(self, request, users: QuerySet):
        choice = self.value()

        match choice:
            case 'yes':
                return users.filter(_subscriptions_count__gt=0)
            case 'no':
                return users.filter(_subscriptions_count=0)
            case _:
                return users


class HasSubscribersFilter(admin.SimpleListFilter):
    title = 'Есть подписчики'
    parameter_name = 'has_subscribers'

    def lookups(self, request, model_admin):
        return (
            ('yes', 'Да'),
            ('no', 'Нет'),
        )

    def queryset(self, request, users: QuerySet):
        choice = self.value()

        match choice:
            case 'yes':
                return users.filter(_subscribers_count__gt=0)
            case 'no':
                return users.filter(_subscribers_count=0)
            case _:
                return users


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    """
    Кастомная админка пользователя
    """

    list_display = (
        'id',
        'username',
        'full_name',
        'email',
        'avatar_html',
        'recipes_count',
        'subscribtions_count',
        'subscribers_count',
        'is_active',
        'is_staff',
    )

    search_fields = ('email', 'username')
    list_filter = (
        'is_active',
        HasRecipesFilter,
        HasSubscriptionsFilter,
        HasSubscribersFilter,
    )

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

    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        users = super().get_queryset(request)
        return users.annotate(
            _recipes_count=Count('recipes', distinct=True),
            _subscribtions_count=Count(
                'from_user_subscriptions',
                distinct=True,
            ),
            _subscribers_count=Count(
                'to_user_subscriptions',
                distinct=True,
            ),
        )

    @admin.display(description='ФИО')
    def full_name(self, user):
        return f'{user.first_name} {user.last_name}'

    @admin.display(description='Аватар')
    def avatar_html(self, user):
        return format_html(
            (
                '<img src="{}" width="80" height="60" '
                'style="object-fit: cover;" />'
            ),
            user.avatar.url,
        )

    @admin.display(description='Число рецептов')
    def recipes_count(self, user):
        return user._recipes_count

    @admin.display(description='Число подписок')
    def subscribtions_count(self, user):
        return user._subscribtions_count

    @admin.display(description='Число подписчиков')
    def subscribers_count(self, user):
        return user._subscribers_count


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('id', 'from_user', 'to_user')
    search_fields = ('from_user__username', 'to_user__username')


@admin.register(Favorite, ShoppingCartItem)
class SaveRecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe')
    search_fields = ('user__username', 'recipe__name')
