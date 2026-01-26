from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.db.models import Count, QuerySet
from django.utils.safestring import mark_safe

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

    def lookups(self, request, model_admin):
        recipes = model_admin.get_queryset(request)

        values = (
            recipes.order_by('cooking_time')
            .values_list('cooking_time', flat=True)
            .distinct()
        )

        if len(values) < 3:
            self.thresholds = {}
            return []

        fast = values[len(values) // 3]
        long = values[(len(values) * 2) // 3]

        self.thresholds = {
            'fast': (1, fast - 1),
            'mid': (fast, long - 1),
            'long': (long, values.last()),
        }

        fast_count = recipes.filter(
            cooking_time__range=self.thresholds['fast']
        ).count()
        mid_count = recipes.filter(
            cooking_time__range=self.thresholds['mid']
        ).count()
        long_count = recipes.filter(
            cooking_time__range=self.thresholds['long']
        ).count()

        return (
            ('fast', f'быстрее {fast} мин ({fast_count})'),
            ('mid', f'быстрее {long} мин ({mid_count})'),
            ('long', f'долго ({long_count})'),
        )

    def queryset(self, request, recipes):
        selected = self.value()
        if selected not in self.thresholds:
            return recipes

        return recipes.filter(cooking_time__range=self.thresholds[selected])


class HasRelatedObjectsFilter(admin.SimpleListFilter):
    """
    Фильтр "Есть связанные объекты".
    Наследники должны задать:
        - title: заголовок фильтра
        - parameter_name: GET-параметр
        - relation_field: атрибут, по которому считаем наличие
        (например, '_recipes_count')
    """

    OPTIONS = (
        ('yes', 'Да'),
        ('no', 'Нет'),
    )

    relation_field: str = None

    def lookups(self, request, model_admin):
        return self.OPTIONS

    def queryset(self, request, queryset: QuerySet):
        selected = self.value()
        if selected == 'yes':
            return queryset.filter(**{f'{self.relation_field}__gt': 0})
        if selected == 'no':
            return queryset.filter(**{f'{self.relation_field}': 0})
        return queryset


class InRecipesFilter(HasRelatedObjectsFilter):
    title = 'Есть в рецептах'
    parameter_name = 'in_recipes'
    relation_field = '_recipes_count'


class HasRecipesFilter(HasRelatedObjectsFilter):
    title = 'Есть рецепты'
    parameter_name = 'has_recipes'
    relation_field = '_recipes_count'


class HasSubscriptionsFilter(HasRelatedObjectsFilter):
    title = 'Есть подписки'
    parameter_name = 'has_subscriptions'
    relation_field = '_subscriptions_count'


class HasSubscribersFilter(HasRelatedObjectsFilter):
    title = 'Есть подписчики'
    parameter_name = 'has_subscribers'
    relation_field = '_subscribers_count'


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
    @mark_safe
    def ingredients_html(self, recipe):
        return '<br>'.join(
            f'{relation.ingredient.name} - {relation.amount} '
            f'{relation.ingredient.measurement_unit}'
            for relation in (
                recipe.recipe_ingredients.select_related('ingredient')
            )
        )

    @admin.display(description='Теги')
    @mark_safe
    def tags_html(self, recipe):
        return '<br>'.join(tag.name for tag in recipe.tags.all())

    @admin.display(description='Фото')
    @mark_safe
    def image_html(self, recipe):
        return (
            f'<img src="{recipe.image.url}" width="80" '
            'height="60" style="object-fit: cover;"/>'
        )


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'recipe', 'ingredient', 'amount')
    search_fields = ('recipe__name', 'ingredient__name')


class RecipesCountMixin(admin.ModelAdmin):
    """Миксин для админок, где нужна колонка с количеством рецептов."""

    list_display = ('recipes_count',)

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .annotate(_recipes_count=Count('recipes', distinct=True))
        )

    @admin.display(description='Число рецептов')
    def recipes_count(self, obj):
        return getattr(obj, '_recipes_count', 0)


@admin.register(Ingredient)
class IngredientAdmin(RecipesCountMixin, admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'measurement_unit',
        *RecipesCountMixin.list_display,
    )
    search_fields = ('name', 'measurement_unit')
    ordering = ('name',)
    list_filter = (InRecipesFilter, 'measurement_unit')


@admin.register(Tag)
class TagAdmin(RecipesCountMixin, admin.ModelAdmin):
    list_display = ('id', 'name', 'slug', *RecipesCountMixin.list_display)
    search_fields = ('name', 'slug')


@admin.register(User)
class UserAdmin(RecipesCountMixin, DjangoUserAdmin):
    """
    Кастомная админка пользователя
    """

    list_display = (
        'id',
        'username',
        'full_name',
        'email',
        'avatar_html',
        'subscribtions_count',
        'subscribers_count',
        *RecipesCountMixin.list_display,
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
            {'fields': ('is_active', 'is_staff', 'is_superuser')},
        ),
        ('Даты', {'fields': ('last_login', 'date_joined')}),
    )

    def get_queryset(self, request):
        users = super().get_queryset(request)
        return users.annotate(
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
    @mark_safe
    def avatar_html(self, user):
        return (
            f'<img src="{user.avatar.url}" width="50" height="50">'
            if user.avatar
            else '—'
        )

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
class UserRecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe')
    search_fields = ('user__username', 'recipe__name')
