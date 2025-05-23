"""Шаблоны url для API."""
# from django.conf import settings
from django.urls import include, path

urlpatterns = [
    path('auth/', include('userprofile.urls')),
    path('', include('recipes.urls')),
]
