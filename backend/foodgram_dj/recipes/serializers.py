"""Сериализаторы для моделей рецептов и ингредиентов."""
from django.utils.translation import gettext_lazy as _
# from django_short_url.urls import
from rest_framework import serializers
from .models import Recipe, Ingredient, IngredientRecipe, Favorites
from image64conv.serializers import Base64ImageField
from userprofile.serializers import UserProfileSerializer


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для ингредиентов."""

    class Meta:
        model = Ingredient
        fields = '__all__'


class IngredientRecipeCreateSerializer(serializers.Serializer):
    """Сериализатор для ввода ингредиентов при создании/обновлении рецепта."""
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField(min_value=1)


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

    ingredients = serializers.SerializerMethodField()

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

    def get_ingredients(self, obj):
        """Метод для получения ингредиентов при чтении."""
        ingredients = obj.recipe_ingredients.all()
        return IngredientRecipeSerializer(ingredients, many=True).data

    def to_internal_value(self, data):
        """Преобразование входных данных перед валидацией."""
        ret = super().to_internal_value(data)
        if 'ingredients' in data:
            ret['ingredients'] = data['ingredients']
        return ret

    def validate_ingredients(self, value):
        """Валидация ингредиентов."""
        if not isinstance(value, list):
            raise serializers.ValidationError(
                "Ингредиенты должны быть списком!")

        if not value:
            raise serializers.ValidationError(
                "Нужен как минимум один ингредиент!")

        ingredient_ids = [item.get('id') for item in value]
        if None in ingredient_ids:
            raise serializers.ValidationError(
                "У каждого ингредиента должен быть id")

        if len(ingredient_ids) != len(set(ingredient_ids)):
            raise serializers.ValidationError(
                "Игредиенты не должны повторяться!")

        return value

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
        """Создание рецепта с ингредиентами."""
        ingredients_data = validated_data.pop('ingredients', [])
        recipe = Recipe.objects.create(**validated_data)

        # Получаем объекты ингредиентов один раз
        ingredient_ids = [item['id'] for item in ingredients_data]
        ingredients = Ingredient.objects.in_bulk(ingredient_ids)

        # Создаем связи с ингредиентами
        ingredient_recipe_objects = [
            IngredientRecipe(
                recipe=recipe,
                ingredient=ingredients[ingredient_data['id']],
                amount=ingredient_data['amount']
            )
            for ingredient_data in ingredients_data
        ]
        IngredientRecipe.objects.bulk_create(ingredient_recipe_objects)

        return recipe

    def update(self, instance, validated_data):
        """Обновление рецепта с ингредиентами."""
        ingredients_data = validated_data.pop('ingredients', None)

        # Обновляем основные поля рецепта
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Обновляем ингредиенты, если они переданы
        if ingredients_data is not None:
            instance.recipe_ingredients.all().delete()
            self._create_ingredients(instance, ingredients_data)

        return instance

    def _create_ingredients(self, recipe, ingredients_data):
        """Создание связей с ингредиентами."""
        ingredient_recipe_objects = [
            IngredientRecipe(
                recipe=recipe,
                ingredient=ingredient_data['id'],
                amount=ingredient_data['amount']
            )
            for ingredient_data in ingredients_data
        ]
        IngredientRecipe.objects.bulk_create(ingredient_recipe_objects)

    def _update_ingredients(self, recipe, ingredients_data):
        """Обновление связей с ингредиентами."""
        # Удаляем старые ингредиенты
        recipe.recipe_ingredients.all().delete()
        # Создаем новые
        self._create_ingredients(recipe, ingredients_data)
