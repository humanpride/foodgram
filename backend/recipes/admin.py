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
            'long': (long, max(values)),
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
        if not hasattr(self, 'thresholds') or not self.thresholds:
            return recipes

        return recipes.filter(
            cooking_time__range=self.thresholds[self.value()]
        )


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
            f'{ingredient.name} - {ingredient.amount} '
            f'{ingredient.measurement_unit}'
            for ingredient in recipe.ingredients.all()
        )

    @admin.display(description='Теги')
    @mark_safe
    def tags_html(self, recipe):
        return '<br>'.join(tag.name for tag in recipe.tags.all())

    @admin.display(description='Фото')
    @mark_safe
    def image_html(self, recipe):
        return (
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


class RelatedCountMixin(admin.ModelAdmin):
    """
    Миксин для добавления полей с количеством связанных объектов.
    Наследник должен определить словарь `related_fields` вида:
        `{
            'field_name': 'related_name',
        }`
    """

    related_fields: dict = {}

    def get_queryset(self, request) -> QuerySet:
        queryset = super().get_queryset(request)
        if self.related_fields:
            annotations = {
                f'_{field}': Count(relation, distinct=True)
                for field, relation in self.related_fields.items()
            }
            queryset = queryset.annotate(**annotations)
        return queryset

    @classmethod
    def _make_display_method(cls, field_name: str, description: str = ''):
        """
        Возвращает метод для отображения аннотированного поля в list_display.
        """

        def _display(obj):
            return getattr(obj, f'_{field_name}', 0)

        _display.short_description = description or field_name
        return _display


@admin.register(Ingredient)
class IngredientAdmin(RelatedCountMixin, admin.ModelAdmin):
    list_display = ('id', 'name', 'measurement_unit', 'recipes_count')
    search_fields = ('name', 'measurement_unit')
    ordering = ('name',)
    list_filter = (InRecipesFilter, 'measurement_unit')
    related_fields = {'recipes_count': 'recipes'}

    recipes_count = RelatedCountMixin._make_display_method(
        'recipes_count', 'Число рецептов'
    )


@admin.register(Tag)
class TagAdmin(RelatedCountMixin, admin.ModelAdmin):
    list_display = ('id', 'name', 'slug', 'recipes_count')
    search_fields = ('name', 'slug')
    related_fields = {'recipes_count': 'recipes'}

    recipes_count = RelatedCountMixin._make_display_method(
        'recipes_count', 'Число рецептов'
    )


@admin.register(User)
class UserAdmin(RelatedCountMixin, DjangoUserAdmin):
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
    )

    related_fields = {
        'recipes_count': 'recipes',
        'subscribtions_count': 'from_user_subscriptions',
        'subscribers_count': 'to_user_subscriptions',
    }

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

    recipes_count = RelatedCountMixin._make_display_method(
        'recipes_count', 'Число рецептов'
    )
    subscribtions_count = RelatedCountMixin._make_display_method(
        'subscribtions_count', 'Число подписок'
    )
    subscribers_count = RelatedCountMixin._make_display_method(
        'subscribers_count', 'Число подписчиков'
    )


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('id', 'from_user', 'to_user')
    search_fields = ('from_user__username', 'to_user__username')


@admin.register(Favorite, ShoppingCartItem)
class UserRecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe')
    search_fields = ('user__username', 'recipe__name')
