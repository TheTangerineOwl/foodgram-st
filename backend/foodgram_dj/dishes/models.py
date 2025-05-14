"""Реализация моделей для рецепта и его ингредиентов."""
from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _

# Получение стандартной модели пользователя для проекта
User = get_user_model()


class Ingredient(models.Model):
    """Модель ингредиента в рецепте блюда."""

    class MeasurementUnit(models.TextChoices):
        """Перечисление возможных единиц измерения для ингредиента."""

        KG = 'kilo', _('кг.')
        GR = 'gr', _('г.')
        LITER = 'liter', _('л.')
        ML = 'ml', _('мл.')
        PIECE = 'pcs', _('шт.')
        TSP = 'teaspoons', _('ч.л.')
        SP = 'spoons', _('ст.л.')

    name = models.CharField('Название', max_length=256)
    measurement_unit = models.CharField(
        'Единица измерения',
        choices=MeasurementUnit,
        default=MeasurementUnit.GRб,
        null=False
    )

    class Meta:
        verbose_name = 'ингредиент'
        verbose_name_plural = 'Ингредиенты'


class Recipe(models.Model):
    """Модель рецепта блюда."""

    name = models.CharField(
        verbose_name='Название',
        max_length=256,
        blank=False
    )
    text = models.TextField(
        verbose_name='Описание',
        blank=False
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления (в минутах)',
        blank=False
    )
    image = models.ImageField(
        verbose_name='Фото',
        upload_to='recipes/images',
        default=None
    )
    author = models.ForeignKey(
        User,
        related_name='recipes',
        on_delete=models.CASCADE
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientRecipe',
        blank=False
    )
    is_favorited = models.BooleanField(
        verbose_name='В Избранном',
        default=False
    )
    is_in_shopping_cart = models.BooleanField(
        verbose_name='В Корзине',
        default=False
    )

    class Meta:
        verbose_name = 'рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        """Строковое представление рецепта его именем."""
        return self.name


class IngredientRecipe(models.Model):
    """Модель для связи рецепта и его ингредиента."""

    recipes = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        blank=False,
        on_delete=models.CASCADE
    )
    ingredient = models.ForeignKey(
        Ingredient,
        verbose_name='Ингредиент',
        blank=False,
        on_delete=models.CASCADE
    )

    def __str__(self):
        """Строковое представление связи."""
        return f'{self.ingredient} {self.recipes}'
