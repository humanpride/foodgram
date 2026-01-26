from django.shortcuts import redirect
from rest_framework.serializers import ValidationError

from recipes.models import Recipe


def recipe_short_redirect(request, recipe_id):
    if not Recipe.objects.filter(id=recipe_id).exists():
        raise ValidationError(
            {'recipe_id': ['Рецепта с id {recipe_id} не найдено.']}
        )
    return redirect(f'/recipes/{recipe_id}/')
