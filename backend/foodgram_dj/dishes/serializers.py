"""Сериализаторы для моделей рецептов и ингредиентов."""
from base64 import b64decode
from django.core.files.base import ContentFile
from rest_framework import serializers

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

    def create(self, validated_data):
        """Валидация и добавление ингредиентов."""
        if 'ingredients' not in self.initial_data:
            raise serializers.ValidationError(
                'Поле "ингредиенты" не может быть пустым!'
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
                'Поле "Ингредиенты" не может быть пустым!'
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
