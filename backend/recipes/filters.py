from django_filters import BaseInFilter, CharFilter
from django_filters import rest_framework as filters

from recipes.models import Recipe
from users.models import Favorite, ShoppingCartItem


class CharInFilter(BaseInFilter, CharFilter):
    pass


class RecipeFilter(filters.FilterSet):
    is_favorited = filters.NumberFilter(method='filter_is_favorited')
    is_in_shopping_cart = filters.NumberFilter(
        method='filter_is_in_shopping_cart'
    )
    author = filters.NumberFilter(field_name='author__id')
    tags = CharInFilter(field_name='tags__slug', lookup_expr='in')

    class Meta:
        model = Recipe
        fields = ['is_favorited', 'is_in_shopping_cart', 'author', 'tags']

    def filter_is_favorited(self, qs, name, value):
        user = getattr(self.request, 'user', None)
        if str(value) == '1':
            if user and user.is_authenticated:
                return qs.filter(
                    pk__in=Favorite.objects.filter(user=user).values_list(
                        'recipe_id', flat=True
                    )
                )
            return qs.none()
        if str(value) == '0':
            if user and user.is_authenticated:
                return qs.exclude(
                    pk__in=Favorite.objects.filter(user=user).values_list(
                        'recipe_id', flat=True
                    )
                )
            return qs
        return qs

    def filter_is_in_shopping_cart(self, qs, name, value):
        user = getattr(self.request, 'user', None)
        if str(value) == '1':
            if user and user.is_authenticated:
                return qs.filter(
                    pk__in=ShoppingCartItem.objects.filter(
                        user=user
                    ).values_list('recipe_id', flat=True)
                )
            return qs.none()
        if str(value) == '0':
            if user and user.is_authenticated:
                return qs.exclude(
                    pk__in=ShoppingCartItem.objects.filter(
                        user=user
                    ).values_list('recipe_id', flat=True)
                )
            return qs
        return qs
