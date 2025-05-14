"""Настройка приложения dishes."""
from django.apps import AppConfig


class DishesConfig(AppConfig):
    """Класс для настройки и регистрации приложения."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'dishes'
    verbose_name = 'Блюда'
