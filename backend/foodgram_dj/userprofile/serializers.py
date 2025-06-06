"""Сериализаторы для модели профиля пользователя."""
from rest_framework.decorators import action
from rest_framework import serializers
from recipes.serializers import Base64ImageField
from djoser.serializers import UserSerializer, UserCreateSerializer
from .models import UserProfile, Subscription


class SubscriptionSerializer(serializers.ModelSerializer):
    """Сериализатор для подписок."""

    class Meta:
        # Метаданные.
        model = Subscription
        read_only_field = ('user', 'follower')


class UserProfileSerializer(UserSerializer):
    """Сериализатор профиля пользователя."""

    is_subscribed = serializers.SerializerMethodField(
        'get_is_subscribed',
        read_only=True
    )
    avatar = Base64ImageField(required=False, allow_null=True)
    avatar_url = serializers.SerializerMethodField(
        'get_avatar_url',
        read_only=True,
    )

    class Meta(UserSerializer.Meta):
        # Метаданные
        model = UserProfile
        fields = '__all__'

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
        current_user = self.get_current_user()
        return Subscription.objects.filter(
            user=current_user, follows=obj).exists()

    @action(detail=True, methods=['put', 'delete'], url_path='avatar')
    def delete_avatar(self, instance, validated_data=None):
        instance.avatar = None
        if validated_data:
            instance.avatar = validated_data.get('avatar', instance.avatar)
        instance.save()
        return instance


class UserProfileCreateSerializer(UserCreateSerializer):
    """Сериализатор для регистрации пользователя."""

    class Meta(UserCreateSerializer.Meta):
        model = UserProfile
        fields = ('id', 'email', 'username', 'password',
                  'first_name', 'last_name', 'avatar')
