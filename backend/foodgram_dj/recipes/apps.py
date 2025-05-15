"""Настройка приложения recipes."""
from django.apps import AppConfig


class RecipesConfig(AppConfig):
    """Класс для настройки и регистрации приложения."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'recipes'
    verbose_name = 'Рецепты'
