"""Модель профиля пользователя, списка покупок и избранного."""
from django.db import models
from django.contrib.auth.models import AbstractUser
# from django.contrib.auth import get_user_model

# Получение стандартной модели пользователя для этого проекта.
# User = get_user_model()


class UserProfile(AbstractUser):
    """Профиль пользователя."""

    email = models.EmailField(
        unique=True,
        max_length=254
    )

    username = models.CharField(
        max_length=150,
        unique=True,
    )

    first_name = models.CharField(
        max_length=150,
        blank=True,
    )

    last_name = models.CharField(
        max_length=150,
        blank=True,
    )

    avatar = models.ImageField(
        'Аватар',
        upload_to='users/images',
        null=True,
        default=None
    )
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = [
        'username',
        'first_name',
        'last_name',
        'password'
    ]

    class Meta(AbstractUser.Meta):
        # Метаданные.
        db_table = 'auth_user'
        verbose_name = 'профиль пользователя'
        verbose_name_plural = 'Профили пользователей'


class Subscription(models.Model):
    """Модель для связи пользователей подпиской."""

    user = models.ForeignKey(
        UserProfile,
        verbose_name='Пользователь',
        related_name='subscriber',
        on_delete=models.CASCADE
    )
    follows = models.ForeignKey(
        UserProfile,
        verbose_name='Подписка',
        related_name='subbed_to',
        on_delete=models.CASCADE
    )

    class Meta:
        # Метаданные
        constraints = [
            models.UniqueConstraint(fields=['user', 'follows'],
                                    name="unique_subs")
        ]
        verbose_name = 'подписка'
        verbose_name_plural = 'Подписки'
