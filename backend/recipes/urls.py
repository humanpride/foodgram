from django.urls import path

from recipes.views import recipe_short_redirect


urlpatterns = [
    path('s/<int:recipe_id>/', recipe_short_redirect, name='recipe-short'),
]
