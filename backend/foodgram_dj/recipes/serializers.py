"""Сериализаторы для моделей рецептов и ингредиентов."""
from django.utils.translation import gettext_lazy as _
# from django_short_url.urls import
from rest_framework import serializers
from .models import Recipe, Ingredient, IngredientRecipe, Favorites
from image64conv.serializers import Base64ImageField
from userprofile.serializers import UserProfileSerializer


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для ингредиентов."""

    # ingredient_name = serializers.CharField(source='name')

    class Meta:
        model = Ingredient
        fields = '__all__'


class IngredientRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для ингредиентов."""

    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.CharField(source='ingredient.name')
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit')

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для рецептов."""

    author = UserProfileSerializer(read_only=True)

    ingredients = IngredientRecipeSerializer(
        many=True,
        source='ingredientrecipe_set'
    )
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
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        return obj.user_favs.filter(user=request.user).exists()

    def get_is_in_shopping_cart(self, obj):
        # return obj.is_in_shopping_cart
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        return obj.shopping_carts.filter(user=request.user).exists()

    def create(self, validated_data):
        """Валидация и добавление ингредиентов."""
        ingredients_data = self.initial_data.get('ingredients', [])
        recipe = Recipe.objects.create(**validated_data)

        for ingredient_data in ingredients_data:
            IngredientRecipe.objects.create(
                recipe=recipe,
                ingredient_id=ingredient_data['id'],
                amount=ingredient_data['amount']
            )
        return recipe

    def update(self, instance, validated_data):
        """Валидация данных при обновлении."""
        ingredients_data = self.initial_data.get('ingredients', [])

        # Обновляем основные поля
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get('cooking_time',
                                                   instance.cooking_time)
        instance.image = validated_data.get('image', instance.image)
        instance.save()

        # Обновляем ингредиенты
        instance.ingredients.clear()
        for ingredient_data in ingredients_data:
            IngredientRecipe.objects.create(
                recipe=instance,
                ingredient_id=ingredient_data['id'],
                amount=ingredient_data['amount']
            )
        return instance
