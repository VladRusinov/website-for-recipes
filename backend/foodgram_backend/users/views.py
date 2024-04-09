from django.shortcuts import get_object_or_404
from djoser.serializers import SetPasswordSerializer
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.validators import ValidationError

from recipes.pagination import CustomPagination
from users.models import Follow, User
from users.serializers import (
    FollowSerializer, CreateUserSerializer, UserSerializer
)


class UserViewSet(viewsets.ModelViewSet):
    """ViewSet модели User."""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = CustomPagination

    def get_serializer_class(self):
        if self.action == 'create':
            return CreateUserSerializer
        return UserSerializer

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated]
    )
    def me(self, request):
        """Текущий пользователь."""
        serializer = UserSerializer(
            self.request.user, context={'request': request}
        )
        return Response(
            data=serializer.data,
            status=status.HTTP_200_OK
        )

    @action(
        detail=False,
        methods=['Post'],
        permission_classes=[IsAuthenticated]
    )
    def set_password(self, request):
        """Изменение пароля текущего пользователя."""
        serializer = SetPasswordSerializer(
            data=request.data,
            context={'request': request}
        )
        if serializer.is_valid(raise_exception=True):
            self.request.user.set_password(serializer.data["new_password"])
            self.request.user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated],
        pagination_class=CustomPagination
    )
    def subscriptions(self, request):
        """Подписки текущего пользователя."""
        following = self.paginate_queryset(
            Follow.objects.filter(user=self.request.user)
        )
        serializer = FollowSerializer(
            following,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def subscribe(self, request, pk):
        """Создание и удаление подписки."""
        following = get_object_or_404(User, id=pk)
        user = self.request.user
        if request.method == 'POST':
            if Follow.objects.filter(following=following, user=user).exists():
                raise ValidationError(
                    'Вы уже подписаны на данного пользователя'
                )
            if user == following:
                raise ValidationError('Нельзя подписываться на себя')
            Follow.objects.create(user=user, following=following)
            serializer = FollowSerializer(
                Follow.objects.filter(user=self.request.user),
                many=True,
                context={'request': request}
            )
            return Response(
                data=serializer.data[0], status=status.HTTP_201_CREATED
            )
        if not Follow.objects.filter(following=following, user=user).exists():
            raise ValidationError('Вы не подписаны на данного пользователя')
        obj = Follow.objects.get(following=following)
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
