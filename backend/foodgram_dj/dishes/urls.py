"""Шаблоны URL для приложения dishes."""
from django.urls import include, path
from rest_framework import routers

# Регистрация маршрутов для recipes и ingredients.
router = routers.DefaultRouter()
# router.register(r'recipes', RecipeViewSet)
# router.register(r'ingredients', IngredientViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
