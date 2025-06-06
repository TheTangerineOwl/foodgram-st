"""Настройка админ-зоны для приложения рецептов и ингредиентов."""
from django.contrib import admin
from .models import Recipe, Ingredient, IngredientRecipe

admin.site.register(Ingredient)
admin.site.register(Recipe)
admin.site.register(IngredientRecipe)

# class IngredientRecipeInline(admin.StackedInline):
#     model = IngredientRecipe
#     # fk_name = 'recipe'
#     extra = 1
#     # autocomplete_fields = ['ingredient']


# @admin.register(Ingredient)
# class IngredientAdmin(admin.ModelAdmin):
#     search_fields = ['name']


# @admin.register(Recipe)
# class RecipeAdmin(admin.ModelAdmin):
#     search_fields = ['name', 'author']
#     inlines = [IngredientRecipeInline, ]
