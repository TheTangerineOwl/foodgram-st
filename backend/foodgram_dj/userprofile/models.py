"""Модель профиля пользователя, списка покупок и избранного."""
from django.db import models
from django.contrib.auth.models import AbstractUser
# from django.contrib.auth import get_user_model

# Получение стандартной модели пользователя для этого проекта.
# User = get_user_model()


class UserProfile(AbstractUser):
    """Профиль пользователя."""

    avatar = models.ImageField(
        'Аватар',
        upload_to='users/images',
        null=True,
        default=None
    )

    class Meta:
        # Метаданные.
        verbose_name = 'профиль пользователя'
        verbose_name_plural = 'Профили пользователей'


class Subscription(models.Model):
    """Модель для связи пользователей подпиской."""

    user = models.ForeignKey(
        UserProfile,
        related_name='Пользователь',
        on_delete=models.CASCADE
    )
    follower = models.ForeignKey(
        UserProfile,
        related_name='Подписка',
        on_delete=models.CASCADE
    )

    class Meta:
        # Метаданные
        constraints = [
            models.UniqueConstraint(fields=['user', 'follower'],
                                    name="unique_subs")
        ]
        verbose_name = 'подписка'
        verbose_name_plural = 'Подписки'
