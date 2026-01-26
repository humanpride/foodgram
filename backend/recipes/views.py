from django.core.exceptions import ValidationError
from django.shortcuts import redirect

from recipes.models import Recipe


def recipe_short_redirect(request, recipe_id):
    if not Recipe.objects.filter(id=recipe_id).exists():
        raise ValidationError(
            {'recipe_id': [f'Рецепта с id {recipe_id} не найдено.']}
        )
    return redirect(f'/recipes/{recipe_id}/')
