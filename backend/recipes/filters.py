from django_filters import BaseInFilter, CharFilter
from django_filters import rest_framework as filters

from recipes.models import Recipe


class CharInFilter(BaseInFilter, CharFilter):
    pass


class RecipeFilter(filters.FilterSet):
    is_favorited = filters.BooleanFilter(field_name='is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(
        field_name='is_in_shopping_cart'
    )
    author = filters.NumberFilter(field_name='author__id')
    tags = CharInFilter(field_name='tags__slug', lookup_expr='in')

    class Meta:
        model = Recipe
        fields = ['is_favorited', 'is_in_shopping_cart', 'author', 'tags']
