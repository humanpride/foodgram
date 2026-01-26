from django.db.models import (
    BooleanField,
    Count,
    Exists,
    OuterRef,
    Prefetch,
    Value,
)
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.serializers import ValidationError

from api import utils
from api.filters import IngrediendFilter, RecipeFilter
from api.pagination import PageLimitPagination
from api.serializers import (
    IngredientSerializer,
    RecipeCreateUpdateSerializer,
    RecipeReadSerializer,
    RecipeShortSerializer,
    SetAvatarSerializer,
    TagSerializer,
    UserSerializer,
    UserWithRecipesSerializer,
)
from recipes.models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCartItem,
    Subscription,
    Tag,
    User,
)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngrediendFilter


class RecipeViewSet(viewsets.ModelViewSet):
    lookup_field = 'id'
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    pagination_class = PageLimitPagination
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        qs = (
            Recipe.objects.all()
            .select_related('author')
            .prefetch_related(
                'tags',
                Prefetch(
                    'recipe_ingredients',
                    queryset=RecipeIngredient.objects.all().select_related(
                        'ingredient'
                    ),
                ),
            )
            .order_by('-created_at')
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

        qs = qs.annotate(favorites_count=Count('favorites', distinct=True))

        return qs

    def get_serializer_class(self):
        if self.action in ('create', 'partial_update', 'update'):
            return RecipeCreateUpdateSerializer
        return RecipeReadSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def _add_to_collection(self, request, id, model):
        """Добавляет рецепт в коллекцию (избранное или корзину)."""
        recipe = self.get_object()
        user = request.user

        obj, created = model.objects.get_or_create(user=user, recipe=recipe)
        if not created:
            raise ValidationError({'detail': f'{recipe} уже добавлен.'})

        return Response(
            RecipeShortSerializer(recipe, context={'request': request}).data,
            status=status.HTTP_201_CREATED,
        )

    def _remove_from_collection(self, id, model):
        get_object_or_404(model, recipe__id=id).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'])
    def favorite(self, request, id):
        return self._add_to_collection(request, id, Favorite)

    @favorite.mapping.delete
    def unfavorite(self, request, id=None):
        return self._remove_from_collection(id, Favorite)

    @action(
        detail=True,
        methods=['post'],
        url_path='shopping_cart',
        url_name='shopping_cart',
    )
    def add_to_shopping_cart(self, request, id):
        return self._add_to_collection(request, id, ShoppingCartItem)

    @add_to_shopping_cart.mapping.delete
    def remove_from_shopping_cart(self, request, id):
        return self._remove_from_collection(id, ShoppingCartItem)

    @action(
        detail=True,
        methods=['get'],
        url_name='get-link',
        url_path='get-link',
        permission_classes=(AllowAny,),
    )
    def get_link(self, request, id):
        """
        Возвращает короткую ссылку на рецепт.

        Формат: `/s/<int:id>`
        """
        return Response(
            {
                'short-link': request.build_absolute_uri(
                    reverse('recipe-short', args=(id,))
                )
            }
        )

    @action(detail=False, methods=['get'])
    def download_shopping_cart(self, request):
        """
        Собирает все рецепты из корзины пользователя, агрегирует продукты
        и отдаёт в виде .txt файла.
        """

        recipes = Recipe.objects.filter(shoppingcartitems__user=request.user)
        return FileResponse(
            render_to_string(
                '../templates/export/shopping_list.html',
                {
                    'aggregated': [
                        {
                            f'{product["ingredient__name"]}': (
                                f' — {product["total_amount"]} '
                                f'{product["ingredient__measurement_unit"]}'
                            )
                        }
                        for product in utils.aggregate_ingredients(recipes)
                    ],
                    'recipes': recipes,
                },
            ),
            as_attachment=True,
            filename='shopping_list.txt',
        )


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name', 'slug')


class UserViewSet(DjoserUserViewSet):
    """Действия:
    - create / list / retrieve
    - me (GET)
    - set_password
    - subscribe / unsubscribe
    """

    queryset = User.objects.all()
    lookup_field = 'id'
    pagination_class = PageLimitPagination
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

    @action(
        detail=False, methods=['get'], permission_classes=[IsAuthenticated]
    )
    def me(self, request):
        return super().me(request)

    @action(
        detail=True, methods=['post'], permission_classes=[IsAuthenticated]
    )
    def subscribe(self, request, id):
        target_user = get_object_or_404(User, id=id)
        current_user = request.user
        if target_user == current_user:
            raise ValidationError({'detail': 'Нельзя подписаться на себя.'})
        _, created = Subscription.objects.get_or_create(
            from_user=current_user, to_user=target_user
        )
        if not created:
            raise ValidationError(
                {'detail': f'Вы уже подписаны на пользователя {target_user}.'},
            )

        return Response(
            UserWithRecipesSerializer(
                target_user,
                context={'request': request},
            ).data,
            status=status.HTTP_201_CREATED,
        )

    @subscribe.mapping.delete
    def unsubscribe(self, request, id):
        get_object_or_404(
            Subscription,
            from_user=request.user,
            to_user__id=id,
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False, methods=['get'], permission_classes=[IsAuthenticated]
    )
    def subscriptions(self, request):
        return self.get_paginated_response(
            UserWithRecipesSerializer(
                self.paginate_queryset(
                    User.objects.filter(
                        id__in=Subscription.objects.filter(
                            from_user=request.user
                        ).values_list('to_user__id', flat=True)
                    )
                ),
                many=True,
                context={'request': request},
            ).data
        )

    @action(
        detail=False,
        methods=['put', 'delete'],
        url_path='me/avatar',
        permission_classes=[IsAuthenticated],
    )
    def set_avatar(self, request):
        if request.method != 'PUT':
            request.user.avatar.delete(save=True)
            return Response(status=status.HTTP_204_NO_CONTENT)
        serializer = SetAvatarSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        return Response(
            {'avatar': request.user.avatar.url}, status=status.HTTP_200_OK
        )
