"""Сериализаторы для моделей рецептов и ингредиентов."""
from django.utils.translation import gettext_lazy as _
# from django_short_url.urls import
from rest_framework import serializers
from .models import Recipe, Ingredient, IngredientRecipe
from image64conv.serializers import Base64ImageField
from userprofile.serializers import UserProfileSerializer


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для ингредиентов."""

    ingredient_name = serializers.CharField(source='name')

    class Meta:
        model = Ingredient
        fields = '__all__'


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для рецептов."""

    author = UserProfileSerializer(read_only=True)
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
        fields = '__all__'
        # read_only_fields

    def get_image_url(self, obj):
        """Получение ссылки на картинку."""
        if obj.image:
            return obj.image.url
        return None

    def get_is_favorited(self, obj):
        obj.is_favorited = False

        return obj.is_favorited

    def get_is_in_shopping_cart(self, obj):
        # return obj.is_in_shopping_cart
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        return obj.shopping_carts.filter(user=request.user).exists()

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
