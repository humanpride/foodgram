from django.shortcuts import get_object_or_404
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from core.permissions import IsAdmin
from users.models import Subscription, User
from users.serializers import (
    SetAvatarSerializer,
    SetPasswordSerializer,
    UserCreateSerializer,
    UserSerializer,
    UserWithRecipesSerializer,
)


class UserViewSet(
    viewsets.GenericViewSet,
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
):
    """
    Действия:
      - create / list / retrieve
      - me (GET)
      - set_password handled elsewhere (or add action)
      - subscribe / unsubscribe
    """

    queryset = User.objects.all()
    lookup_field = 'id'

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        if self.action == 'subscriptions':
            return UserWithRecipesSerializer
        return UserSerializer

    def get_permissions(self):
        if self.action in (
            'me',
            'set_avatar',
            'subscribe',
            'subscriptions',
            'unsubscribe',
        ):
            perm_classes = [IsAuthenticated]
        elif self.action in ('partial_update', 'destroy'):
            perm_classes = [IsAdmin]
        else:
            perm_classes = [AllowAny]
        return [p() for p in perm_classes]

    @action(detail=False, methods=['get'])
    def me(self, request):
        serializer = UserSerializer(request.user, context={'request': request})
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def subscribe(self, request, id=None):
        target = get_object_or_404(User, id=id)
        user = request.user
        if target == user:
            return Response(
                {'detail': 'Cannot subscribe to self.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if Subscription.objects.filter(
            from_user=user, to_user=target
        ).exists():
            return Response(
                {'detail': 'Already subscribed.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        Subscription.objects.create(from_user=user, to_user=target)
        serializer = UserWithRecipesSerializer(
            target, context={'request': request}
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @subscribe.mapping.delete
    def unsubscribe(self, request, id=None):
        target = get_object_or_404(User, id=id)
        user = request.user
        deleted, _ = Subscription.objects.filter(
            from_user=user, to_user=target
        ).delete()
        if not deleted:
            return Response(
                {'detail': 'Not subscribed.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'])
    def subscriptions(self, request):
        qs = User.objects.filter(subscription__from_user=request.user)
        page = self.paginate_queryset(qs)
        if page:
            serializer = UserWithRecipesSerializer(
                page, many=True, context={'request': request}
            )
            return self.get_paginated_response(serializer.data)
        serializer = UserWithRecipesSerializer(
            qs, many=True, context={'request': request}
        )
        return Response(serializer.data)

    @action(detail=False, methods=['put', 'delete'], url_path='me/avatar')
    def set_avatar(self, request):
        # PUT to set avatar, DELETE to remove
        if request.method == 'PUT':
            serializer = SetAvatarSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(user=request.user)
            return Response(
                {'avatar': request.user.avatar.url}, status=status.HTTP_200_OK
            )
        else:
            # DELETE
            request.user.avatar.delete(save=True)
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=['post'],
        permission_classes=[IsAuthenticated],
    )
    def set_password(self, request):
        serializer = SetPasswordSerializer(
            data=request.data, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
