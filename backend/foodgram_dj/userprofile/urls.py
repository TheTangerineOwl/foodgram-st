"""Шаблоны url для аутентификации."""
# from django.conf import settings
from django.urls import include, path

urlpatterns = [
    path('', include('djoser.urls')),
    path('', include('djoser.urls.jwt')),
]
