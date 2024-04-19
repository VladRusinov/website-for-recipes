from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (
    IsAuthenticated, IsAuthenticatedOrReadOnly
)
from rest_framework.response import Response
from rest_framework.validators import ValidationError

from recipes.filters import IngredientsSearch, RecipeFilter
from recipes.models import (
    Ingredient,
    IngredientRecipe,
    Favorite,
    Recipe,
    ShoppingCart,
    Tag,
)
from recipes.pagination import Pagination
from recipes.permissions import IsAuthorOrReadOnly
from recipes.serializers import (
    FavoriteSerializer,
    GetRecipeSerializer,
    IngredientSerializer,
    PostRecipeSerializer,
    ShoppingCartSerializer,
    TagSerializer,
)
from recipes.utils import download


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet модели Ingredient."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (IngredientsSearch,)
    search_fields = ('^name',)
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    """ViewSet модели Recipe."""

    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    pagination_class = Pagination
    permission_classes = (IsAuthorOrReadOnly, IsAuthenticatedOrReadOnly)

    def get_queryset(self):
        return Recipe.objects.all()

    def get_serializer_class(self):
        if self.request.method not in permissions.SAFE_METHODS:
            return PostRecipeSerializer
        return GetRecipeSerializer

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def favorite(self, request, pk):
        """Избранное."""
        message = 'избранное'
        if request.method == 'POST':
            return self.add_recipe(request, pk, FavoriteSerializer)
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
            return self.add_recipe(request, pk, ShoppingCartSerializer)
        return self.delete_recipe(request, pk, ShoppingCart, message)

    @action(
        detail=False,
        methods=['get', ],
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

    def add_recipe(self, request, pk, serializer_class):
        """Добавить рецепт в избранное или список покупок."""
        data = {
            'user': request.user.id,
            'recipe': pk
        }
        serializer = serializer_class(
            data=data, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete_recipe(self, request, pk, model, message):
        """Удалить рецепт из избранного или списка покупок."""
        recipe = get_object_or_404(Recipe, pk=pk)
        user = self.request.user
        if not model.objects.filter(user=user, recipe=recipe).exists():
            raise ValidationError(f'Рецепт не добавлен в {message}')
        obj = get_object_or_404(model, recipe=recipe, user=user)
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet модели Tag."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
