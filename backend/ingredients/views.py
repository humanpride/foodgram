from rest_framework import viewsets
from rest_framework.permissions import AllowAny

from ingredients.models import Ingredient
from ingredients.serializers import IngredientSerializer


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        qs = super().get_queryset()
        name = self.request.query_params.get('name')
        if not name:
            return qs
        # startswith case-insensitive
        starts = qs.filter(name__istartswith=name)
        # optional: contains for fallback, order startsfirst then contains
        contains = qs.filter(name__icontains=name).exclude(
            id__in=starts.values_list('id', flat=True)
        )
        return starts.union(contains) if contains.exists() else starts
