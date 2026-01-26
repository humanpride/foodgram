from django.db.models import QuerySet, Sum

from recipes.models import RecipeIngredient


def aggregate_ingredients(recipes: QuerySet):
    return (
        RecipeIngredient.objects.filter(
            recipe__id__in=recipes.values_list('id', flat=True)
        )
        .values(
            'ingredient__id',
            'ingredient__name',
            'ingredient__measurement_unit',
        )
        .annotate(total_amount=Sum('amount'))
        .order_by('ingredient__name')
    )
