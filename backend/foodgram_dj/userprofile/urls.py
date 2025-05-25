"""Шаблоны url для аутентификации."""
# from django.conf import settings
from django.urls import include, path

urlpatterns = [

    # path('users/subscriptions/'),
    # path('users/<int:pk>/subsribe/'),
    path('', include('djoser.urls')),
    path('', include('djoser.urls.jwt')),
]
