from django.urls import include, path
from django.views.generic import RedirectView
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework.routers import DefaultRouter

from ingredients.views import IngredientViewSet
from recipes.views import RecipeViewSet
from tags.views import TagViewSet
from users.views import UserViewSet


router = DefaultRouter()
router.register('users', UserViewSet, basename='user')
router.register('recipes', RecipeViewSet, basename='recipe')
router.register('ingredients', IngredientViewSet, basename='ingredient')
router.register('tags', TagViewSet, basename='tag')

urlpatterns = [
    # DRF token login
    path('api/auth/token/login/', obtain_auth_token, name='token_login'),
    # You may want a logout endpoint which deletes token,
    # implement separately if needed.
    path('api/', include(router.urls)),
    # example short link redirect (optional) — redirect to recipe detail
    path(
        's/<int:pk>/',
        RedirectView.as_view(pattern_name='recipe-detail', permanent=False),
    ),
]
