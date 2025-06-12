"""Шаблоны url для API."""
from django.urls import include, path

urlpatterns = [
    # Эндпоинты для рецептов и подписок
    path('', include('recipes.urls')),
    path('', include('userprofile.urls')),  # Эндпоинты для пользователя
]
