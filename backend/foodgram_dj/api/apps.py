"""Настройка приложения API."""
from django.apps import AppConfig


class ApiConfig(AppConfig):
    """Класс для настройки приложения API."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'
    verbose_name = 'API'
