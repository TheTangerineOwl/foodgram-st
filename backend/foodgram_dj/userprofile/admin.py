"""Настройка админ-зоны для приложения userorofile."""
from django.contrib import admin
from .models import UserProfile  # , Subscription

admin.register(UserProfile)
