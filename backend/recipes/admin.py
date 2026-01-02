from django.contrib import admin
from django.db.models import Count

from .models import Recipe, RecipeIngredient


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'author',
        'favorites_count',
    )

    search_fields = ('name', 'author__username')
    list_filter = ('tags',)
    inlines = (RecipeIngredientInline,)

    def get_queryset(self, request):
        # добавляем annotate для подсчёта избранных
        queryset = super().get_queryset(request)
        return queryset.annotate(
            _favorites_count=Count('favorited_by', distinct=True)
        )

    @admin.display(description='В избранном')
    def favorites_count(self, obj):
        return obj._favorites_count


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'recipe', 'ingredient', 'amount')
    search_fields = ('recipe__name', 'ingredient__name')
