"""Настройка админ-зоны для приложения userorofile."""
from django.contrib import admin
from .models import UserProfile, Subscription

admin.site.register(UserProfile)
admin.site.register(Subscription)
