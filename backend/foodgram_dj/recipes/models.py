"""Реализация моделей для рецепта и его ингредиентов."""
from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.urls import reverse

# Получение стандартной модели пользователя для проекта
User = get_user_model()


class Ingredient(models.Model):
    """Модель ингредиента в рецепте блюда."""

    name = models.CharField(_('Название'), max_length=256)
    measurement_unit = models.CharField(
        _('Единица измерения'),
        default=_('г.'),
        null=False,
        max_length=30
    )

    class Meta:
        ordering = ['name', ]
        verbose_name = _('ингредиент')
        verbose_name_plural = _('Ингредиенты')

    def __str__(self):
        return self.name + ', ' + self.measurement_unit


class Recipe(models.Model):
    """Модель рецепта блюда."""

    name = models.CharField(
        verbose_name=_('Название'),
        max_length=256,
        blank=False
    )
    text = models.TextField(
        verbose_name=_('Описание'),
        blank=False
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name=_('Время приготовления (в минутах)'),
        blank=False
    )
    image = models.ImageField(
        verbose_name=_('Фото'),
        upload_to='recipes/images',
        blank=True,
        default=None
    )
    author = models.ForeignKey(
        User,
        related_name='recipes',
        verbose_name=_('Автор'),
        on_delete=models.CASCADE
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientRecipe',
        verbose_name=_('Игредиенты'),
        related_name='recipes',  # для доступа из ингредиента
        through_fields=('recipe', 'ingredient'),
        blank=False,
    )
    created_at = models.DateTimeField(
        'Добавлено',
        auto_now_add=True
    )

    class Meta:
        verbose_name = _('рецепт')
        verbose_name_plural = _('Рецепты')

    def __str__(self):
        """Строковое представление рецепта его именем."""
        return self.name

    def get_absolute_url(self):
        return reverse('recipe-detail', kwargs={'pk': self.pk})


class IngredientRecipe(models.Model):
    """Модель для связи рецепта и его ингредиента."""
    recipe = models.ForeignKey(
        Recipe,
        verbose_name=_('Рецепт'),
        blank=False,
        on_delete=models.CASCADE
    )
    ingredient = models.ForeignKey(
        Ingredient,
        verbose_name=_('Ингредиент'),
        blank=False,
        on_delete=models.CASCADE
    )
    amount = models.IntegerField(
        _('Количество'),
        blank=False
    )

    def __str__(self):
        """Строковое представление связи."""
        return f'{self.ingredient} {self.recipe}'

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_recipe_ingredient'
            )
        ]
        default_related_name = 'recipe_ingredients'


class ShoppingCart(models.Model):
    """Модель списка покупок."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='cart',
        verbose_name='Пользователь',
        null=False
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shopping_carts',
        verbose_name='Рецепт',
        null=False
    )

    class Meta:
        verbose_name = 'список покупок'
        verbose_name = 'Списки покупок'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'user'],
                name='unique_recipe_user'
            )
        ]

    def __str__(self):
        return f'{self.recipe} в корзине {self.user}'


class Favorites(models.Model):
    """Модель списка избранных рецептов."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favs',
        verbose_name='Пользователь',
        null=False
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='user_favs',
        verbose_name='Рецепт',
        null=False
    )

    class Meta:
        verbose_name = 'избранное'
        verbose_name = 'Избранное'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'user'],
                name='unique_recipe_user_fav'
            )
        ]

    def __str__(self):
        return f'{self.recipe} в избранном {self.user}'
