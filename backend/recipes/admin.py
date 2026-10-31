from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.contrib.auth.models import Group
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


admin.site.unregister(Group)


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    fk_name = 'recipe'
    extra = 1


class CookingTimeHistogramFilter(admin.SimpleListFilter):
    title = 'Cooking time'
    parameter_name = 'cooking_time_bin'

    def lookups(self, request, model_admin):
        recipes = model_admin.get_queryset(request)

        values = (
            recipes.order_by('cooking_time')
            .values_list('cooking_time', flat=True)
            .distinct()
        )

        if len(values) < 3:
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
            ('fast', f'under {fast} min ({fast_count})'),
            ('mid', f'under {long} min ({mid_count})'),
            ('long', f'long ({long_count})'),
        )

    def queryset(self, request, recipes):
        selected = self.value()
        if selected not in self.thresholds:
            return recipes

        return recipes.filter(cooking_time__range=self.thresholds[selected])


class HasRelatedObjectsFilter(admin.SimpleListFilter):
    """
    "Has related objects" filter.
    Subclasses must define:
        - title: filter title
        - parameter_name: GET parameter
        - relation_field: attribute used to check for related objects
        (for example, '_recipes_count')
    """

    OPTIONS = (
        ('yes', 'Yes'),
        ('no', 'No'),
    )

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
    title = 'Used in recipes'
    parameter_name = 'in_recipes'
    relation_field = '_recipes_count'


class HasRecipesFilter(HasRelatedObjectsFilter):
    title = 'Has recipes'
    parameter_name = 'has_recipes'
    relation_field = '_recipes_count'


class HasSubscriptionsFilter(HasRelatedObjectsFilter):
    title = 'Follows users'
    parameter_name = 'has_subscriptions'
    relation_field = '_subscriptions_count'


class HasSubscribersFilter(HasRelatedObjectsFilter):
    title = 'Has followers'
    parameter_name = 'has_subscribers'
    relation_field = '_subscribers_count'


class ImagePreviewAdminMixin:
    """
    Django Admin mixin:
    add a fieldset containing the image field and its preview
    """

    image_field = 'image'
    image_preview_field = 'image_preview'
    image_fieldset_title = 'Image'
    image_preview_description = 'Preview'

    # --- PREVIEW ---
    @admin.display(description=image_preview_description)
    @mark_safe
    def image_preview(self, obj):
        image = getattr(obj, self.image_field, None)
        if image:
            return (
                f'<img src="{image.url}" '
                'style="max-width: 200px; max-height: 200px;" />'
            )
        return 'No image'

    def get_readonly_fields(self, request, obj=None):
        return (
            *super().get_readonly_fields(request, obj),
            self.image_preview_field,
        )

    def get_fieldsets(self, request, obj=None):
        return (
            *super().get_fieldsets(request, obj),
            (
                self.image_fieldset_title,
                {
                    'fields': (
                        self.image_field,
                        self.image_preview_field,
                    )
                },
            ),
        )


@admin.register(Recipe)
class RecipeAdmin(ImagePreviewAdminMixin, admin.ModelAdmin):
    image_field = 'image'
    image_fieldset_title = 'Recipe photo'
    image_preview_description = 'Photo preview'

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

    fieldsets = (
        (
            None,
            {'fields': ('name', 'author', 'tags', 'cooking_time', 'text')},
        ),
    )

    def get_queryset(self, request):
        recipes = super().get_queryset(request)
        return recipes.annotate(
            _favorites_count=Count('favorites', distinct=True)
        )

    @admin.display(description='In favorites')
    def favorites_count(self, recipe):
        return recipe._favorites_count

    @admin.display(description='Ingredients')
    @mark_safe
    def ingredients_html(self, recipe):
        return '<br>'.join(
            f'{relation.ingredient.name} - {relation.amount} '
            f'{relation.ingredient.measurement_unit}'
            for relation in recipe.recipe_ingredients.select_related(
                'ingredient'
            )
        )

    @admin.display(description='Tags')
    @mark_safe
    def tags_html(self, recipe):
        return '<br>'.join(tag.name for tag in recipe.tags.all())

    @admin.display(description='Photo')
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
    """Mixin for admin classes that need a recipe count column."""

    list_display = ('recipes_count',)

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .annotate(_recipes_count=Count('recipes', distinct=True))
        )

    @admin.display(description='Recipe count')
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
class UserAdmin(RecipesCountMixin, ImagePreviewAdminMixin, DjangoUserAdmin):
    image_field = 'avatar'
    image_fieldset_title = 'Avatar'
    image_preview_description = 'Avatar preview'

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

    readonly_fields = ('avatar_preview',)

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
            'Personal information',
            {
                'fields': (
                    'email',
                    'first_name',
                    'last_name',
                )
            },
        ),
        (
            'Permissions',
            {'fields': ('is_active', 'is_staff', 'is_superuser')},
        ),
        ('Dates', {'fields': ('last_login', 'date_joined')}),
    )

    def get_queryset(self, request):
        users = super().get_queryset(request)
        return users.annotate(
            _subscriptions_count=Count(
                'from_user_subscriptions',
                distinct=True,
            ),
            _subscribers_count=Count(
                'to_user_subscriptions',
                distinct=True,
            ),
        )

    @admin.display(description='Avatar preview')
    @mark_safe
    def avatar_preview(self, user):
        if user.avatar:
            return (
                f'<img src="{user.avatar.url}" '
                f'style="max-height: 200px; max-width: 200px;" />'
            )
        return 'No avatar'

    @admin.display(description='Full name')
    def full_name(self, user):
        return f'{user.first_name} {user.last_name}'

    @admin.display(description='Avatar')
    @mark_safe
    def avatar_html(self, user):
        return (
            f'<img src="{user.avatar.url}" width="50" height="50">'
            if user.avatar
            else '—'
        )

    @admin.display(description='Following count')
    def subscribtions_count(self, user):
        return user._subscriptions_count

    @admin.display(description='Follower count')
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
