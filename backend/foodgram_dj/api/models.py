"""Модели для использования в API."""
from django.db import models
from django.contrib.auth import get_user_model

# Получение стандартной модели пользователя для этого проекта.
User = get_user_model()


class UserProfile(models.Model):
    """Модель профиля, расширяющая модель пользователя."""
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь'
    )
    is_subscribed = models.BooleanField(
        'Подписан',
        default=False
    )
    avatar = models.ImageField(
        'Аватар',
        upload_to='users/images',
        null=True,
        default=None
    )

    class Meta:
        verbose_name = 'профиль пользователя'
        verbose_name_plural = 'Профили пользователей'
