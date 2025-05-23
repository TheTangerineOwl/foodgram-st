"""Настройка приложения userprofile."""
from django.apps import AppConfig


class UserProfileConfig(AppConfig):
    """Класс для настройки приложения."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'userprofile'
