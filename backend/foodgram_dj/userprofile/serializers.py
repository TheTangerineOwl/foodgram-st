"""Сериализаторы для модели профиля пользователя."""
from rest_framework import serializers, status
from django.shortcuts import get_object_or_404
from recipes.serializers import Base64ImageField
from djoser.serializers import UserSerializer
from .models import UserProfile, Subscription


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
            user=current_user, follows=obj).exists()


class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        read_only_field = ('user', 'follows')

    def create(self, validated_data):
        user = UserProfileSerializer.get_current_user()
        if user is None:
            return status.HTTP_401_UNAUTHORIZED
        if 'follows' not in self.initial_data:
            raise serializers.ValidationError(
                'Поле "Подписка" не может быть пустым!'
            )
        pk = validated_data.pop('follows')
        follows = get_object_or_404(UserProfile, pk=pk)
        sub = Subscription.objects.get(user=user, follows=follows)
        if sub is not None:
            return status.HTTP_400_BAD_REQUEST
        return super().create(validated_data)
