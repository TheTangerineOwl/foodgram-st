"""Сериализаторы для моделей рецептов и ингредиентов."""
from base64 import b64decode
from django.core.files.base import ContentFile
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _
from django_short_url.views import get_surl
from django_short_url.models import ShortURL
# from django_short_url.urls import 
from rest_framework import serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status

from .models import Recipe, Ingredient, IngredientRecipe


class Base64ImageField(serializers.ImageField):
    """Поле для представления картинки в формате base64."""

    def to_internal_value(self, data):
        """
        Переводит представление картинки из base64-строки в указанный формат.
        """
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для ингредиентов."""

    ingredient_name = serializers.CharField(source='name')

    class Meta:
        model = Ingredient


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для рецептов."""

    ingredients = IngredientSerializer(many=True, required=True)
    image = Base64ImageField(required=False, allow_null=True)
    image_url = serializers.SerializerMethodField(
        'get_image_url',
        read_only=True,
    )
    is_favorited = serializers.SerializerMethodField(
        'get_is_favorited',
        read_only=True
    )
    is_in_shopping_cart = serializers.SerializerMethodField(
        'get_is_in_shopping_cart',
        read_only=True
    )

    class Meta:
        # Имена для использования в админ-зоне.
        model = Recipe
        # fields = (, )
        # read_only_fields

    def get_image_url(self, obj):
        """Получение ссылки на картинку."""
        if obj.image:
            return obj.image.url
        return None

    def get_is_favorited(self, obj):
        is_favorited = False

        return is_favorited

    def get_is_in_shopping_cart(self, obj):
        is_in_shopping_cart = False

        return is_in_shopping_cart

    def create(self, validated_data):
        """Валидация и добавление ингредиентов."""
        if 'ingredients' not in self.initial_data:
            raise serializers.ValidationError(
                _('Поле "ингредиенты" не может быть пустым!')
            )
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        for ingredient in ingredients:
            current_ingredient, status = Ingredient.objects.get_or_create(
                **ingredient
            )
            IngredientRecipe.objects.create(
                ingredient=current_ingredient, recipe=recipe
            )
        return recipe

    def update(self, instance, validated_data):
        """Валидация данных при обновлении."""
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time',
            instance.cooking_time
        )
        instance.image = validated_data.get('image', instance.image)

        if 'ingredients' not in validated_data:
            raise serializers.ValidationError(
                _('Поле "Ингредиенты" не может быть пустым!')
            )

        ingredients_data = validated_data.pop('ingredients')
        lst = []
        for ingredient in ingredients_data:
            current, status = Ingredient.objects.get_or_create(
                **ingredient
            )
            lst.append(current)
        instance.achievements.set(lst)
        instance.save()
        return instance

    @action(detail=True, methods=['get'], url_path='get-link')
    def get_short_link(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)

        # Создаем полный URL для рецепта
        full_url = request.build_absolute_uri(recipe.get_absolute_url())

        # Создаем или получаем существующую короткую ссылку
        # short_url, created = ShortURL.objects.get_or_create(url=full_url)
        short_url = get_surl(full_url)

        # Возвращаем короткую ссылку
        return Response({
            'short-link': short_url
        }, status=status.HTTP_200_OK)

    def redirect_short_url(request, short_url):
        """Перенаправляет короткую ссылку на оригинальный URL."""
        url = get_surl(short_url)
        return HttpResponseRedirect(url)
