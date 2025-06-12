"""Фильтры для приложения recipes."""
from .models import Recipe
from django_filters import rest_framework as filters


class RecipeFilter(filters.FilterSet):
    """Фильтр для рецептов."""
    is_favorited = filters.BooleanFilter(method='filter_is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_in_shopping_cart')

    class Meta:
        model = Recipe
        fields = ['author', 'name']

    def filter_is_favorited(self, queryset, name, value):
        """Возвращает список рецептов из Избранного данного пользователя."""
        if value and self.request.user.is_authenticated:
            return queryset.filter(user_favs__user=self.request.user)
        return queryset

    def filter_in_shopping_cart(self, queryset, name, value):
        """Возвращает список рецептов из Корзины данного пользователя."""
        if value and self.request.user.is_authenticated:
            return queryset.filter(shopping_carts__user=self.request.user)
        return queryset
