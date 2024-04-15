from colorfield.fields import ColorField

from django.core.validators import MinValueValidator
from django.db import models

from users.constants import (
    LETTER_LIMIT, MIN_VALUE, RECIPES_MAX_LENGTH
)
from users.models import User


class Tag(models.Model):
    """Модель тега."""

    name = models.CharField(
        'Название', max_length=RECIPES_MAX_LENGTH, unique=True
    )
    color = ColorField(
        'Цвет в HEX', format="hexa", unique=True
    )
    slug = models.SlugField('Слаг', unique=True, max_length=RECIPES_MAX_LENGTH)

    class Meta:
        ordering = ['id']
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name[:LETTER_LIMIT]


class Ingredient(models.Model):
    """Модель ингредиента."""

    name = models.CharField('Название', max_length=RECIPES_MAX_LENGTH)
    measurement_unit = models.CharField(
        'Единица измерения', max_length=RECIPES_MAX_LENGTH
    )

    class Meta:
        ordering = ['id']
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        constraints = [
            models.UniqueConstraint(
                fields=['name', ' measurement_unit'], name='unique_measurement'
            ),
        ]

    def __str__(self):
        return self.name[:LETTER_LIMIT]


class Recipe(models.Model):
    """Модель рецепта."""

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор'
    )
    name = models.CharField('Название', max_length=RECIPES_MAX_LENGTH)
    image = models.ImageField(
        upload_to='recipes/images/',
        verbose_name='Изображение'
    )
    text = models.TextField('Описание рецепта')
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='Ингредиенты',
    )
    tags = models.ManyToManyField(Tag, verbose_name='Тег')
    cooking_time = models.PositiveSmallIntegerField(
        'Время приготовления',
        validators=[MinValueValidator(MIN_VALUE)]
    )
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        default_related_name = 'recipes'

    def __str__(self):
        return self.name[:LETTER_LIMIT]


class IngredientRecipe(models.Model):
    """Модель ингредиентов для конкретного рецепта."""

    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент',
        related_name='recipes_ingredients'
    )
    amount = models.PositiveSmallIntegerField(
        'Колличество',
        validators=[MinValueValidator(MIN_VALUE)]
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='ingredient_recipes'
    )

    class Meta:
        ordering = ['id']
        verbose_name = 'Ингредиент для рецепта'
        verbose_name_plural = 'Ингредиенты для рецепта'

    def __str__(self):
        return f'{self.ingredient} - {self.recipe}'[:LETTER_LIMIT]


class Favorite(models.Model):
    """Модель избранного."""
    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        on_delete=models.CASCADE
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        on_delete=models.CASCADE
    )

    class Meta:
        ordering = ['id']
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        default_related_name = 'favorites'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'], name='unique_favorite'
            ),
        ]

    def __str__(self):
        return f'{self.user} - {self.recipe}'[:LETTER_LIMIT]


class ShoppingCart(models.Model):
    """Модель списка покупок."""

    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        on_delete=models.CASCADE
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        on_delete=models.CASCADE
    )

    class Meta:
        ordering = ['id']
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        default_related_name = 'shopping_carts'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'], name='unique_shopping_cart'
            ),
        ]

    def __str__(self):
        return f'{self.user} - {self.recipe}'[:LETTER_LIMIT]
