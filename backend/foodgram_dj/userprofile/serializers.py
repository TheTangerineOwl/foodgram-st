"""Сериализаторы для модели профиля пользователя."""
from rest_framework.decorators import action
from rest_framework import serializers
from recipes.serializers import Base64ImageField
from djoser.serializers import UserSerializer
from .models import UserProfile, Subscription


class SubscriptionSerializer(serializers.ModelSerializer):
    """Сериализатор для подписок."""

    class Meta:
        # Метаданные.
        model = Subscription
        read_only_field = ('user', 'follower')


class UserProfileSerializer(UserSerializer):
    """Сериализатор профиля пользователя."""

    is_subsribed = serializers.SerializerMethodField(
        'get_is_subsribed',
        read_only=True
    )
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

    def get_current_user(self):
        """Получение текущего авторизованного пользователя."""
        request = self.context.get('request', None)
        if request:
            return request.user

    def get_is_subscribed(self, obj):
        """
        Получает значение, подписан ли текущий пользователь на выбранного.
        """
        current_user = self.get_current_user()
        return Subscription.objects.filter(
            user=current_user, subscriber=obj).exists()

    @action(detail=True, methods=['delete'], url_path='avatar')
    def delete_avatar(self, request, pk=None):
        user = self.get_object()

    @action(method=['put'], url_path='avatar')
    def put_avatar(self, instance, validated_data):
        instance.avatar = validated_data.get('avatar', instance.avatar)
        instance.save()
        return instance
