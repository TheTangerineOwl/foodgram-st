"""Настройка админ-зоны для приложения рецептов и ингредиентов."""
from django.contrib import admin
from .models import Recipe, Ingredient


admin.register(Recipe)
admin.register(Ingredient)
