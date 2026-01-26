from django.db.models import Case, IntegerField, Q, QuerySet, Value, When
from django_filters import BaseInFilter, CharFilter
from django_filters import rest_framework as filters

from recipes.models import Ingredient, Recipe


class CharInFilter(BaseInFilter, CharFilter):
    pass


class RecipeFilter(filters.FilterSet):
    is_favorited = filters.BooleanFilter(field_name='is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(
        field_name='is_in_shopping_cart'
    )
    author = filters.NumberFilter(field_name='author__id')
    tags = filters.CharFilter(method='filter_tags')

    class Meta:
        model = Recipe
        fields = ('is_favorited', 'is_in_shopping_cart', 'author', 'tags')

    def filter_tags(
        self, recipes: QuerySet, field_name: str, value: str
    ) -> QuerySet:
        raw = self.data.getlist(field_name)
        if not raw:
            raw = [tag.strip() for tag in value.split(',')]

        if not raw:
            return recipes

        return recipes.filter(tags__slug__in=raw)


class IngrediendFilter(filters.FilterSet):
    name = CharFilter(
        field_name='name',
        method='filter_with_q',
        label='Фильтрация (istartswith + icontains)',
    )

    class Meta:
        model = Ingredient
        fields = ('name',)

    def filter_with_q(
        self, queryset: QuerySet, field_name: str, value: str
    ) -> QuerySet:
        if not value:
            return queryset

        lookup_starts = {f'{field_name}__istartswith': value}
        lookup_contains = {f'{field_name}__icontains': value}

        return (
            queryset.filter(Q(**lookup_starts) | Q(**lookup_contains))
            .annotate(
                match_order=Case(
                    When(**lookup_starts, then=Value(0)),
                    When(**lookup_contains, then=Value(1)),
                    default=Value(2),
                    output_field=IntegerField(),
                )
            )
            .order_by('match_order', field_name)
        )
