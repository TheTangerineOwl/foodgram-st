"""Представления для приложения dishes."""
# from django.shortcuts import render
# from .models import Recipe, Ingredient

from rest_framework import viewsets, permissions, filters
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from .models import Recipe, Ingredient
from .serializers import IngredientSerializer, RecipeSerializer
from .permissions import AuthorOrReadOnly


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Представление для получения одного ингредиента или списка по поиску."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    search_fields = ('name', )
    # pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    """Представление для получения рецепта."""
    queryset = Recipe.objects.all().order_by('created_at')
    serializer_class = RecipeSerializer
    pagination_class = PageNumberPagination
    permission_classes = (AuthorOrReadOnly,)
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    # filterset_fields = ('author', )
    search_fields = ('name',)
    filterset_fields = ('author',
                        'name', 'is_in_shopping_cart', 'is_favorited')

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
