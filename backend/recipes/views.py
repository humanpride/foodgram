from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
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

    queryset = Recipe.objects.all()
    queryset = queryset.select_related('author').prefetch_related('tags')
    lookup_field = 'id'
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

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

    # def get_queryset(self):
    #     """
    #     Реализация фильтров:
    #       - is_favorited=1
    #       - is_in_shopping_cart=1
    #       - author=[id]
    #       - tags=[slug list], пример `tags=breakfast&tags=lunch`

    #     Фильтрация через query_params.
    #     """
    #     qs = super().get_queryset()

    #     request = self.request
    #     params = request.query_params

    #     # author filter
    #     author = params.get('author')
    #     if author:
    #         qs = qs.filter(author__id=author)

    #     # tags by slug (multiple)
    #     tags = params.getlist('tags')
    #     if tags:
    #         qs = qs.filter(tags__slug__in=tags).distinct()

    #     # is_favorited
    #     is_fav = params.get('is_favorited')
    #     if is_fav in ('1', '0'):  # if is_fav==None: do nothing
    #         if is_fav == '1':
    #             if request.user.is_authenticated:
    #                 qs = qs.filter(favorite__user=request.user)
    #             else:
    #                 qs = qs.none()  # anon can't have favorites
    #         elif request.user.is_authenticated:
    #             # exclude favorites
    #             qs = qs.exclude(favorite__user=request.user)

    #     # is_in_shopping_cart
    #     is_cart = params.get('is_in_shopping_cart')
    #     if is_cart in ('1', '0'):
    #         if is_cart == '1':
    #             if request.user.is_authenticated:
    #                 qs = qs.filter(shoppingcartitem__user=request.user)
    #             else:
    #                 qs = qs.none()
    #         elif request.user.is_authenticated:
    #             qs = qs.exclude(shoppingcartitem__user=request.user)

    #     return qs.distinct()

    @action(
        detail=True,
        methods=['post'],
        # url_path='favorite',
        # url_name='favorite',
    )
    def favorite(self, request, id=None):
        recipe = get_object_or_404(Recipe, id=id)
        user = request.user
        if Favorite.objects.filter(user=user, recipe=recipe).exists():
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
        recipe = get_object_or_404(Recipe, id=id)
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
        recipe = get_object_or_404(Recipe, id=id)
        user = request.user
        if ShoppingCartItem.objects.filter(user=user, recipe=recipe).exists():
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
        recipe = get_object_or_404(Recipe, id=id)
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

    @action(
        detail=True,
        methods=['get'],
        permission_classes=[AllowAny],
        # url_path='get-link',
        # url_name='get_link',
    )
    def get_link(self, request, id=None):
        """
        Возвращает короткую ссылку на рецепт.
        Если у вас есть модель ShortLink — используйте её.

        Здесь простая реализация:
        `https://<host>/s/<recipe_id>`
        """
        recipe = get_object_or_404(Recipe, id=id)
        short = request.build_absolute_uri(f'/s/{recipe.id}')
        return Response({'short-link': short})

    @action(
        detail=False,
        methods=['get'],
        # url_path='download_shopping_cart',
        # url_name='download_shopping_cart',
    )
    def download_shopping_cart(self, request):
        """
        Собирает все рецепты из корзины пользователя, агрегирует ингредиенты
        и отдаёт в виде text/plain.
        """
        user = request.user
        if not user.is_authenticated:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        recipe_ids = ShoppingCartItem.objects.filter(user=user).values_list(
            'recipe_id', flat=True
        )
        if not recipe_ids:
            return HttpResponse(
                'Ваша корзина пуста.\n', content_type='text/plain'
            )

        # группировка по ingredient id, суммирование amounts
        aggregation = (
            RecipeIngredient.objects.filter(recipe_id__in=list(recipe_ids))
            .values('ingredient__name', 'ingredient__measurement_unit')
            .annotate(total_amount=Sum('amount'))
            .order_by('ingredient__name')
        )

        lines = []
        for row in aggregation:
            lines.append(
                f'{row["ingredient__name"]} — '
                f'{row["total_amount"]} '
                f'{row["ingredient__measurement_unit"]}'
            )
        response = HttpResponse('\n'.join(lines), content_type='text/plain')
        response['Content-Disposition'] = (
            'attachment; filename=shopping_list.txt'
        )
        return response
