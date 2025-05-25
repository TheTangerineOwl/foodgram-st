"""Представления для приложения dishes."""
# from django.shortcuts import render
# from .models import Recipe, Ingredient

# Create your views here.
from rest_framework import viewsets, permissions
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
    # pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    """Представление для получения рецепта."""
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    pagination_class = PageNumberPagination
    permission_classes = (AuthorOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('author', 'is_favorited', 'is_in_shopping_cart')

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
