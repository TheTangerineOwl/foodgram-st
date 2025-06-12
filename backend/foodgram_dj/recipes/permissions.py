"""Разрешения для модели recipes."""
from rest_framework import permissions


class AuthorOrReadOnly(permissions.BasePermission):
    """Разрешение для рецепта."""

    def has_permission(self, request, view):
        """Общие разрешения."""
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        """Разрешения для объекта."""
        return (obj.author == request.user
                or request.method in permissions.SAFE_METHODS)
