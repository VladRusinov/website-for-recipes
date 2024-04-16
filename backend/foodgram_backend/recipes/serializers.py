from rest_framework import serializers

from drf_extra_fields.fields import Base64ImageField

from recipes.models import (
    Ingredient,
    IngredientRecipe,
    Favorite,
    Recipe,
    ShoppingCart,
    Tag,
)
from users.serializers import UserSerializer


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор модели Ingredient."""

    class Meta:
        model = Ingredient
        fields = '__all__'


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор модели Tag."""

    class Meta:
        model = Tag
        fields = '__all__'


class IngredientRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор модели IngredientRecipe."""

    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


class AddIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для добавления ингредиента в рецепт."""

    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField()

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'amount')

    def validate(self, data):
        if data['amount'] <= 0:
            raise serializers.ValidationError(
                'Колличество ингредиентов должно быть больше 0'
            )
        return data


class PostRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для Post запроса модели Recipe."""

    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all()
    )
    ingredients = AddIngredientSerializer(many=True)
    author = UserSerializer(read_only=True)
    image = Base64ImageField()

    def create(self, validated_data):
        ingredients = validated_data.pop("ingredients")
        tags = validated_data.pop("tags")
        recipe = Recipe.objects.create(**validated_data)
        ing_recipes = []
        for ingredient in ingredients:
            if ingredient['amount'] <= 0:
                raise serializers.ValidationError(
                    'Колличество ингредиентов должно быть больше 0'
                )
            ingredient_recipe = IngredientRecipe(
                ingredient=ingredient['id'],
                recipe=recipe,
                amount=ingredient['amount']
            )
            ing_recipes.append(ingredient_recipe)
        IngredientRecipe.objects.bulk_create(ing_recipes)
        recipe.tags.set(tags)
        return recipe

    def update(self, instance, validated_data):
        """Обновение рецепта."""
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        instance.ingredients.clear()
        for ingredient in ingredients:
            IngredientRecipe.objects.create(
                ingredient=ingredient['id'],
                recipe=instance,
                amount=ingredient['amount']
            )
        instance.tags.set(tags)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        serializer = super().to_representation(instance)
        serializer['ingredients'] = IngredientRecipeSerializer(
            instance.ingredient_recipes.all(), many=True
        ).data
        serializer['tags'] = TagSerializer(instance.tags.all(), many=True).data
        return serializer

    def validate(self, data):
        """Валидация."""
        if 'ingredients' not in data:
            raise serializers.ValidationError('Добавьте ингредиенты')
        if 'tags' not in data:
            raise serializers.ValidationError('Добавьте теги')
        if len(set(data['tags'])) != len(data['tags']):
            raise serializers.ValidationError(
                'нельзя добавлять одинаковые теги'
            )
        if len(
            set([ingredient['id'] for ingredient in data['ingredients']])
        ) != len([ingredient['id'] for ingredient in data['ingredients']]):
            raise serializers.ValidationError(
                'нельзя добавлять одинаковые ингредиенты'
            )
        if len(data['tags']) == 0 or len(data['ingredients']) == 0:
            raise serializers.ValidationError(
                'нельзя создать рецепт без ингредиентов или тега'
            )
        if data['image'] is None:
            raise serializers.ValidationError('Добавьте изображение')
        return data

    class Meta:
        model = Recipe
        exclude = ('pub_date',)


class GetRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для GET запроса модели Recipe."""

    tags = TagSerializer(many=True, read_only=True)
    author = UserSerializer(read_only=True)
    ingredients = IngredientRecipeSerializer(
        many=True,
        read_only=True,
        source='ingredient_recipes',
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    def get_is_favorited(self, obj):
        """Проверка того, находится ли рецепт в избранном."""
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Favorite.objects.filter(recipe=obj, user=user).exists()

    def get_is_in_shopping_cart(self, obj):
        """Проверка того, находится ли рецепт в списке покупок."""
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(recipe=obj, user=user).exists()

    class Meta:
        model = Recipe
        exclude = ('pub_date',)


class FavoriteSerializer(serializers.ModelSerializer):
    """Сериализатор модели Favorite."""

    name = serializers.CharField(
        source='recipe.name',
        read_only=True
    )
    image = serializers.ImageField(
        source='recipe.image',
        read_only=True
    )
    cooking_time = serializers.IntegerField(
        source='recipe.cooking_time',
        read_only=True
    )
    id = serializers.PrimaryKeyRelatedField(
        source='recipe',
        read_only=True
    )

    class Meta:
        model = Favorite
        fields = ('id', 'name', 'image', 'cooking_time')


class ShoppingCartSerializer(serializers.ModelSerializer):
    """Сериализатор модели ShoppingCart."""

    name = serializers.CharField(
        source='recipe.name',
        read_only=True
    )
    image = serializers.ImageField(
        source='recipe.image',
        read_only=True
    )
    cooking_time = serializers.IntegerField(
        source='recipe.cooking_time',
        read_only=True
    )
    id = serializers.PrimaryKeyRelatedField(
        source='recipe',
        read_only=True
    )

    class Meta:
        model = ShoppingCart
        fields = ('id', 'name', 'image', 'cooking_time')
