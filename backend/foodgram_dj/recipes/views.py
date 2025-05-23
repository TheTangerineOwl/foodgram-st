"""Представления для приложения dishes."""
# from django.shortcuts import render
# from .models import Recipe, Ingredient

# Create your views here.
from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination
from .models import Recipe, Ingredient
from .serializers import IngredientSerializer, RecipeSerializer


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Представление для получения одного ингредиента или списка по поиску."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    """Представление для получения рецепта."""
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    pagination_class = PageNumberPagination

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
