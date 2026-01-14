from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets

from core.filters import IngrediendFilter
from ingredients.models import Ingredient
from ingredients.serializers import IngredientSerializer


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngrediendFilter
