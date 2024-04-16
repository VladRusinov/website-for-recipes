from rest_framework import serializers

from drf_extra_fields.fields import Base64ImageField

from recipes.models import (
    Ingredient,
    IngredientRecipe,
    Recipe,
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

    class Meta:
        model = Recipe
        exclude = ('pub_date',)

    def add_ingredient(self, obj, ingredients):
        """Добавление игредиентов."""
        ing_recipes = []
        for ingredient in ingredients:
            ingredient_recipe = IngredientRecipe(
                ingredient=ingredient['id'],
                recipe=obj,
                amount=ingredient['amount']
            )
            ing_recipes.append(ingredient_recipe)
        return IngredientRecipe.objects.bulk_create(ing_recipes)

    def create(self, validated_data):
        ingredients = validated_data.pop("ingredients")
        tags = validated_data.pop("tags")
        author = self.context.get('request').user
        recipe = Recipe.objects.create(author=author, **validated_data)
        self.add_ingredient(recipe, ingredients)
        recipe.tags.set(tags)
        return recipe

    def update(self, instance, validated_data):
        """Обновение рецепта."""
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        instance.ingredients.clear()
        self.add_ingredient(instance, ingredients)
        instance.tags.set(tags)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return GetRecipeSerializer(instance, context=context).data

    def validate(self, data):
        """Валидация."""
        ingredients = [ingredient['id'] for ingredient in data['ingredients']]
        if len(data['tags']) == 0 or len(data['ingredients']) == 0:
            raise serializers.ValidationError(
                'нельзя создать рецепт без ингредиентов или тега'
            )
        if 'ingredients' not in data:
            raise serializers.ValidationError('Добавьте ингредиенты')
        if 'tags' not in data:
            raise serializers.ValidationError('Добавьте теги')
        if len(set(data['tags'])) != len(data['tags']):
            raise serializers.ValidationError(
                'нельзя добавлять одинаковые теги'
            )
        if len(set(ingredients)) != len(ingredients):
            raise serializers.ValidationError(
                'нельзя добавлять одинаковые ингредиенты'
            )
        if data['image'] is None:
            raise serializers.ValidationError('Добавьте изображение')
        return data


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

    class Meta:
        model = Recipe
        exclude = ('pub_date',)

    def get_is_favorited(self, obj):
        """Проверка того, находится ли рецепт в избранном."""
        user = self.context.get('request').user
        return (
            user.is_authenticated
            and user.favorites.filter(recipe=obj).exists()
        )

    def get_is_in_shopping_cart(self, obj):
        """Проверка того, находится ли рецепт в списке покупок."""
        user = self.context.get('request').user
        return (
            user.is_authenticated
            and user.shopping_carts.filter(recipe=obj).exists()
        )
