from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from core.permissions import IsAuthorOrAdmin
from recipes.filters import RecipeFilter
from recipes.models import Recipe, RecipeIngredient
from recipes.serializers import (
    RecipeCreateSerializer,
    RecipeDetailSerializer,
    RecipeListSerializer,
    RecipeUpdateSerializer,
)
from users.models import Favorite, ShoppingCartItem


class RecipeViewSet(viewsets.ModelViewSet):
    """
    ViewSet для Recipe.
    - list/retrieve доступны всем (AllowAny)
    - create доступен авторизованным
    - partial_update/delete — автор или админ
    Доп. actions: favorite, shopping_cart, get-link, download_shopping_cart
    """

    lookup_field = 'id'
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    filterset_class = RecipeFilter
    search_fileds = (
        '^name',
        'name',
        'author__first_name',
        'author__last_name',
    )

    def get_queryset(self):
        from django.db.models import (
            BooleanField,
            Count,
            Exists,
            OuterRef,
            Prefetch,
            Value,
        )

        qs = (
            Recipe.objects.all()
            .select_related('author')
            .prefetch_related(
                'tags',
                Prefetch(
                    'recipe_ingredients',
                    queryset=RecipeIngredient.objects.select_related(
                        'ingredient'
                    ),
                ),
            )
        )

        user = self.request.user
        if user.is_authenticated:
            favorite_qs = Favorite.objects.filter(
                user=user, recipe=OuterRef('pk')
            )
            cart_qs = ShoppingCartItem.objects.filter(
                user=user, recipe=OuterRef('pk')
            )
            qs = qs.annotate(
                is_favorited=Exists(favorite_qs),
                is_in_shopping_cart=Exists(cart_qs),
            )
        else:
            # анонимному пользователю — False по обоим полям
            qs = qs.annotate(
                is_favorited=Value(False, output_field=BooleanField()),
                is_in_shopping_cart=Value(False, output_field=BooleanField()),
            )

        qs = qs.annotate(favorites_count=Count('favorited_by', distinct=True))

        return qs

    def get_permissions(self):
        if self.action in ('partial_update', 'update', 'destroy'):
            permission_classes = [IsAuthorOrAdmin]
        elif self.action in (
            'create',
            'download_shopping_cart',
            'favorite',
            'shopping_cart',
        ):
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [AllowAny]
        return [p() for p in permission_classes]

    def get_serializer_class(self):
        if self.action == 'create':
            return RecipeCreateSerializer
        if self.action in ('partial_update', 'update'):
            return RecipeUpdateSerializer
        if self.action == 'retrieve':
            return RecipeDetailSerializer
        return RecipeListSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=['post'])
    def favorite(self, request, id=None):
        recipe = self.get_object()
        user = request.user
        if recipe.is_favorited:
            return Response(
                {'detail': 'Already in favorites.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        Favorite.objects.create(user=user, recipe=recipe)

        # возвращаем краткое представление рецепта
        return Response(
            RecipeListSerializer(recipe, context={'request': request}).data,
            status=status.HTTP_201_CREATED,
        )

    @favorite.mapping.delete
    def unfavorite(self, request, id=None):
        recipe = self.get_object()
        user = request.user
        deleted, _ = Favorite.objects.filter(user=user, recipe=recipe).delete()
        if not deleted:
            return Response(
                {'detail': 'Not in favorites.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=['post'],
        url_path='shopping_cart',
        url_name='shopping_cart',
    )
    def add_to_shopping_cart(self, request, id=None):
        recipe = self.get_object()
        user = request.user
        if recipe.is_in_shopping_cart:
            return Response(
                {'detail': 'Already in shopping cart.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        ShoppingCartItem.objects.create(user=user, recipe=recipe)

        return Response(
            RecipeListSerializer(recipe, context={'request': request}).data,
            status=status.HTTP_201_CREATED,
        )

    @add_to_shopping_cart.mapping.delete
    def remove_from_shopping_cart(self, request, id=None):
        recipe = self.get_object()
        user = request.user
        deleted, _ = ShoppingCartItem.objects.filter(
            user=user, recipe=recipe
        ).delete()
        if not deleted:
            return Response(
                {'detail': 'Not in shopping cart.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['get'])
    def get_link(self, request, id=None):
        """
        Возвращает короткую ссылку на рецепт.

        Здесь простая реализация:
        `https://<host>/s/<recipe_id>`
        """
        recipe = self.get_object()
        short = request.build_absolute_uri(f'/s/{recipe.id}')
        return Response({'short-link': short})

    @action(detail=False, methods=['get'])
    def download_shopping_cart(self, request):
        """
        Собирает все рецепты из корзины пользователя, агрегирует ингредиенты
        и отдаёт в виде text/csv/pdf в зависимости от query_params.

        Query params: ?format=pdf | csv | txt (по умолчанию txt)
        """
        from export import utils

        response_format = request.query_params.get('format', 'txt').lower()
        aggregated = utils.build_aggregated_ingredients(request.user)

        if response_format in ('pdf', 'application/pdf'):
            return utils.build_pdf_response(aggregated, request)
        if response_format in ('csv', 'text/csv'):
            return utils.build_csv_response(aggregated)
        return utils.build_text_response(aggregated)
