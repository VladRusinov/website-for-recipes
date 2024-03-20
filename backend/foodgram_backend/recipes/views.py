from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.serializers import SetPasswordSerializer
from rest_framework import mixins, status, viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import (IsAuthenticated)
from rest_framework.validators import ValidationError

from recipes.filters import IngredientsCustomSearch, RecipeFilter
from recipes.models import (
    Ingredient,
    IngredientRecipe,
    Favorite,
    Follow,
    Recipe,
    ShoppingCart,
    Tag,
    User
)
from recipes.serializers import (
    CreateUserSerializer,
    GetRecipeSerializer,
    IngredientRecipeSerializer,
    IngredientSerializer,
    FavoriteSerializer,
    FollowSerializer,
    PostRecipeSerializer,
    ShoppingCartSerializer,
    TagSerializer,
    UserSerializer
)
from recipes.pagination import CustomPagination
from recipes.permissions import IsAuthorOrReadOnly
from recipes.utils import download


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


class IngredientViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    """ViewSet модели Ingredient."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (IngredientsCustomSearch,)
    search_fields = ('^name',)
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    """ViewSet модели Recipe."""

    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    pagination_class = CustomPagination
    permission_classes = (IsAuthorOrReadOnly,)

    def get_queryset(self):
        return Recipe.objects.all()

    def get_serializer_class(self):
        if self.action == 'create':
            return PostRecipeSerializer
        return GetRecipeSerializer

    def perform_create(self, serializer):
        """Сохранение автора рецепта."""
        serializer.save(author=self.request.user)

    @action(
            detail=True,
            methods=['post', 'delete'],
            permission_classes=[IsAuthenticated]
    )
    def favorite(self, request, pk):
        """Избранное."""
        message = 'избранное'
        if request.method == 'POST':
            return self.add_recipe(
                request, pk, Favorite, FavoriteSerializer, message
            )
        else:
            return self.delete_recipe(request, pk, Favorite, message)

    @action(
            detail=True,
            methods=['post', 'delete'],
            permission_classes=[IsAuthenticated]
    )
    def shopping_cart(self, request, pk):
        """Список покупок."""
        message = 'список покупок'
        if request.method == 'POST':
            return self.add_recipe(
                request, pk, ShoppingCart, ShoppingCartSerializer, message
            )
        else:
            return self.delete_recipe(request, pk, ShoppingCart, message)

    @action(
            detail=False,
            methods=['get',],
            permission_classes=[IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        """Скачать список покупок."""
        recipes = [obj.recipe for obj in ShoppingCart.objects.filter(
            user=request.user
        )]
        ingredients = []
        for id in range(len(recipes)):
            ingredients.append(
                IngredientRecipe.objects.filter(recipe=recipes[id])
            )
        return download(ingredients)

    def add_recipe(self, request, pk, model, serializer_class, message):
        """Добавить рецепт в избранное или список покупок."""
        if Recipe.objects.last().id < int(pk):
            raise ValidationError('Рецепта с таким id не существует')
        recipe = Recipe.objects.get(pk=pk)
        user = self.request.user
        if model.objects.filter(recipe=recipe, user=user).exists():
            raise ValidationError(f'Рецепт уже добавлен в {message}')
        serializer = serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save(user=user, recipe=recipe)
        return Response(
            data=serializer.data,
            status=status.HTTP_201_CREATED
        )

    def delete_recipe(self, request, pk, model, message):
        """Удалить рецепт из избранного или списка покупок."""
        recipe = get_object_or_404(Recipe, pk=pk)
        user = self.request.user
        if not model.objects.filter(user=user, recipe=recipe).exists():
            raise ValidationError(f'Рецепт не добавлен в {message}')
        obj = get_object_or_404(model, recipe=recipe, user=user)
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TagViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    """ViewSet модели Tag."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientRecipeViewSet(viewsets.ModelViewSet):
    """ViewSet модели IngredientRecipe."""

    queryset = IngredientRecipe.objects.all()
    serializer_class = IngredientRecipeSerializer
