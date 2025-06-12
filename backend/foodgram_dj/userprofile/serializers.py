"""Сериализаторы для модели профиля пользователя."""
from rest_framework import serializers
from image64conv.serializers import Base64ImageField
from djoser.serializers import UserSerializer, UserCreateSerializer
from .models import UserProfile, Subscription


class UserProfileSerializer(UserSerializer):
    """Сериализатор профиля пользователя."""

    is_subscribed = serializers.SerializerMethodField(
        'get_is_subscribed',
        read_only=True
    )
    avatar = Base64ImageField(required=False, allow_null=True)

    class Meta(UserSerializer.Meta):
        # Метаданные
        model = UserProfile
        fields = ['id', 'email',
                  'username', 'first_name',
                  'last_name', 'is_subscribed',
                  'avatar']

    def get_avatar_url(self, obj):
        """Получение ссылки на картинку-аватар."""
        if obj.avatar:
            return obj.avatar.url
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
        request = self.context.get('request')
        if (not request
           or not request.user.is_authenticated
           or obj == request.user):
            return False
        return Subscription.objects.filter(user=request.user,
                                           follows=obj).exists()


class UserProfileCreateSerializer(UserCreateSerializer):
    """Сериализатор для регистрации пользователя."""

    class Meta(UserCreateSerializer.Meta):
        model = UserProfile
        fields = ('id', 'email', 'username', 'password',
                  'first_name', 'last_name')
