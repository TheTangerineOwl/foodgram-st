"""Шаблоны url для API."""
# from django.conf import settings
from django.urls import include, path

urlpatterns = [
    path('', include('dishes.urls')),
    path('', include('djoser.urls')),
    path('', include('djoser.urls.authtoken')),
]
