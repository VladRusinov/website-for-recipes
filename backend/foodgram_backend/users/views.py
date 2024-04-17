from django.shortcuts import get_object_or_404
from djoser.serializers import SetPasswordSerializer
from rest_framework import status, viewsets, views
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from users.models import Follow, User
from recipes.pagination import Pagination
from users.serializers import (
    CreateUserSerializer,
    SubscribeSerializer,
    SubscriptionSerializer,
    UserSerializer
)


class UserViewSet(viewsets.ModelViewSet):
    """ViewSet модели User."""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = Pagination

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
        serializer.is_valid(raise_exception=True)
        self.request.user.set_password(serializer.data["new_password"])
        self.request.user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class SubscriptionViewSet(ListAPIView):
    """ViewSet модели Subscription."""

    serializer_class = SubscriptionSerializer
    pagination_class = Pagination
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        user = self.request.user
        return user.follow.all()


class SubscribeView(views.APIView):
    """ViewSet модели Subscribe."""

    pagination_class = Pagination
    permission_classes = (IsAuthenticated,)

    def post(self, request, pk):
        following = get_object_or_404(User, pk=pk)
        user = self.request.user
        data = {'following': following.id, 'user': user.id}
        serializer = SubscribeSerializer(
            data=data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            data=serializer.data, status=status.HTTP_201_CREATED
        )

    def delete(self, request, pk):
        following = get_object_or_404(User, pk=pk)
        user = self.request.user
        subscription = get_object_or_404(
            Follow, user=user, following=following
        )
        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
