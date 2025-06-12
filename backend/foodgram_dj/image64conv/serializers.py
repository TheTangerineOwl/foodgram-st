"""
Поля для сериализаторов, позволяющие использовать представление
картинки в base64.
"""
from base64 import b64decode
import uuid
from django.core.files.base import ContentFile
from rest_framework import serializers


class Base64ImageField(serializers.ImageField):
    """Поле для представления картинки в формате base64."""

    def to_internal_value(self, data):
        """
        Переводит представление картинки из base64-строки в указанный формат.
        """
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            filename = f"pic_{uuid.uuid4().hex[:8]}.{ext}"
            data = ContentFile(b64decode(imgstr), name=filename)

        return super().to_internal_value(data)
