from django.shortcuts import redirect

from recipes.models import Recipe


def recipe_short_redirect(request, recipe_id):
    if not Recipe.objects.filter(id=recipe_id).exists():
        return redirect('/')
    return redirect(f'/recipes/{recipe_id}/')
