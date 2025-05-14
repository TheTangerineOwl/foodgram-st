"""Сериализаторы для моделей API."""
from rest_framework import serializers
from dishes.serializers import Base64ImageField
from .models import UserProfile


class UserProfileSerializer(serializers.ModelSerializer):
    """Сериализатор профиля пользователя."""

    avatar = Base64ImageField(required=False, allow_null=True)
    avatar_url = serializers.SerializerMethodField(
        'get_image_url',
        read_only=True,
    )

    class Meta:
        # Метаданные
        model = UserProfile
        read_only_field = (
            'user',
            'is_subsribed')

    def get_image_url(self, obj):
        """Получение ссылки на картинку-аватар."""
        if obj.image:
            return obj.image.url
        return None
