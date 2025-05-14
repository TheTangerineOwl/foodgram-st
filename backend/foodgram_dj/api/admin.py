"""Настройка админ-зоны для API."""
from django.contrib import admin
from .models import User, UserProfile

# Register your models here.
admin.register(User)
admin.register(UserProfile)
