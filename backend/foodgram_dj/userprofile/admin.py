"""Настройка админ-зоны для приложения userorofile."""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import UserProfile, Subscription


class SubscriptionInline(admin.StackedInline):
    """Инлайн для отображения подписок пользователя."""
    model = Subscription
    fk_name = 'user'
    extra = 1
    verbose_name = 'Подписка'
    verbose_name_plural = 'Подписки'

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "follows":
            # Получаем текущего пользователя, которого редактируем
            user_id = request.resolver_match.kwargs.get('object_id')
            if user_id:
                # Исключаем самого пользователя из возможных подписок
                kwargs["queryset"] = UserProfile.objects.exclude(id=user_id)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(UserProfile)
class UserProfileAdmin(UserAdmin):
    """Настройки админки для модели пользователя."""
    list_display = ('username', 'email', 'first_name', 'last_name')
    search_fields = ('username', 'email')
    list_filter = ('username', 'email')
    empty_value_display = '-пусто-'

    # Добавляем инлайн подписок
    inlines = (SubscriptionInline,)

    def get_inline_instances(self, request, obj=None):
        """Инлайны появляются только при редактировании."""
        if not obj:
            return []
        return super().get_inline_instances(request, obj)
