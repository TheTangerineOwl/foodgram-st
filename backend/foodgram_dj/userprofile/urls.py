"""Шаблоны url для аутентификации."""
# from django.conf import settings
from django.urls import include, path

urlpatterns = [

    # path('users/subscriptions/'),
    # path('users/<int:pk>/subsribe/'),
    path('', include('djoser.urls.base')),
    path('auth/', include('djoser.urls.authtoken')),
    path('auth/', include('djoser.urls.jwt')),
]
