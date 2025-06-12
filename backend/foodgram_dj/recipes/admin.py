"""Настройка админ-зоны для приложения рецептов и ингредиентов."""
from django.contrib import admin
from django.db.models import Count
from .models import (Recipe,
                     Ingredient,
                     IngredientRecipe,
                     ShoppingCart,
                     Favorites
                     )


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Настройки админки для модели ингредиентов."""
    list_display = ('name', 'measurement_unit')
    search_fields = ('name',)
    list_filter = ('name',)
    empty_value_display = '-пусто-'


class IngredientRecipeInline(admin.StackedInline):
    """Инлайн для отображения ингредиентов в рецепте."""
    model = IngredientRecipe
    extra = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Настройки админки для модели рецептов."""
    list_display = ('name', 'author', 'favorites_count')
    search_fields = ('name', 'author__username')
    list_filter = ('name', 'author__username')
    inlines = (IngredientRecipeInline,)
    empty_value_display = '-пусто-'

    @admin.display(description='Добавлений в избранное')
    def favorites_count(self, obj):
        return obj.user_favs.count()

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.annotate(
            _favorites_count=Count('user_favs')
        ).order_by('-_favorites_count')


# @admin.register(IngredientRecipe)
# class IngredientRecipeAdmin(admin.ModelAdmin):
#     """Настройки админки для связи ингредиентов и рецептов."""
#     list_display = ('recipe', 'ingredient', 'amount')
#     search_fields = ('recipe__name', 'ingredient__name')
#     empty_value_display = '-пусто-'


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    """Настройки админки для списка покупок."""
    list_display = ('user', 'recipe')
    search_fields = ('user__username', 'recipe__name')
    empty_value_display = '-пусто-'


@admin.register(Favorites)
class FavoritesAdmin(admin.ModelAdmin):
    """Настройки админки для избранных рецептов."""
    list_display = ('user', 'recipe')
    search_fields = ('user__username', 'recipe__name')
    empty_value_display = '-пусто-'
