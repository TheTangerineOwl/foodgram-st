"""Модели для использования в API."""
# from django.db import models
from django.contrib.auth import get_user_model

# Получение стандартной модели пользователя для этого проекта.
User = get_user_model()
