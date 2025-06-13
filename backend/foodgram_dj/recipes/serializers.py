"""Сериализаторы для моделей рецептов и ингредиентов."""
from django.core.paginator import Paginator
from rest_framework import serializers
from .models import Recipe, Ingredient, IngredientRecipe
from image64conv.serializers import Base64ImageField
from userprofile.serializers import UserProfileSerializer


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для ингредиентов."""

    class Meta:
        model = Ingredient
        fields = '__all__'


class IngredientRecipeCreateSerializer(serializers.Serializer):
    """Сериализатор для ввода ингредиентов при создании/обновлении рецепта."""
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
        source='ingredient'
    )
    amount = serializers.IntegerField(
        min_value=1,
        error_messages={
            'min_value': 'Количество должно быть больше нуля!'
        }
    )


class IngredientRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для ингредиентов."""

    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.CharField(source='ingredient.name')
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit')
    amount = serializers.IntegerField()

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для рецептов."""

    cooking_time = serializers.IntegerField(
        min_value=1,
        error_messages={
            'min_value': 'Время приготовления должно быть больше нуля!'
        }
    )

    author = UserProfileSerializer(read_only=True)

    ingredients = IngredientRecipeCreateSerializer(many=True, write_only=True)

    image = Base64ImageField(required=True)

    is_favorited = serializers.SerializerMethodField(
        'get_is_favorited',
        read_only=True
    )
    is_in_shopping_cart = serializers.SerializerMethodField(
        'get_is_in_shopping_cart',
        read_only=True
    )

    class Meta:
        model = Recipe
        fields = ('id', 'author',
                  'ingredients', 'is_favorited',
                  'is_in_shopping_cart',
                  'name', 'image', 'text', 'cooking_time')
        read_only_fields = ('is_favorited',
                            'is_in_shopping_cart', 'author')

    def to_representation(self, instance):
        """Кастомное представление для чтения."""
        representation = super().to_representation(instance)
        representation['ingredients'] = IngredientRecipeSerializer(
            instance.recipe_ingredients.all(), many=True
        ).data
        return representation

    def validate_ingredients(self, value):
        """Валидация ингредиентов."""
        if not isinstance(value, list):
            raise serializers.ValidationError(
                "Ингредиенты должны быть списком!")

        if not value:
            raise serializers.ValidationError(
                "Нужен как минимум один ингредиент!")

        ingredient_ids = [item['ingredient'].id for item in value]
        if None in ingredient_ids:
            raise serializers.ValidationError(
                "У каждого ингредиента должен быть id")

        if len(ingredient_ids) != len(set(ingredient_ids)):
            raise serializers.ValidationError(
                "Игредиенты не должны повторяться!")

        return value

    def get_is_favorited(self, obj):
        """Получение пометки "В Избранном"."""
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        return obj.user_favs.filter(user=request.user).exists()

    def get_is_in_shopping_cart(self, obj):
        """Получение пометки "В Корзине"."""
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        return obj.shopping_carts.filter(user=request.user).exists()

    def create(self, validated_data):
        """Создание рецепта с ингредиентами."""
        ingredients_data = validated_data.pop('ingredients', [])
        recipe = Recipe.objects.create(**validated_data)

        ingredient_recipe_objects = []
        for ingredient_data in ingredients_data:
            ingredient_recipe_objects.append(
                IngredientRecipe(
                    recipe=recipe,
                    ingredient=ingredient_data['ingredient'],
                    amount=ingredient_data['amount']
                )
            )

        IngredientRecipe.objects.bulk_create(ingredient_recipe_objects)
        return recipe

    def update(self, instance, validated_data):
        """Обновление рецепта с ингредиентами."""
        ingredients_data = validated_data.pop('ingredients', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if ingredients_data is not None:
            instance.recipe_ingredients.all().delete()
            ingredient_recipe_objects = []
            for ingredient_data in ingredients_data:
                ingredient_recipe_objects.append(
                    IngredientRecipe(
                        recipe=instance,
                        ingredient=ingredient_data['ingredient'],
                        amount=ingredient_data['amount']
                    )
                )
            IngredientRecipe.objects.bulk_create(ingredient_recipe_objects)

        return instance


class ShortRecipeSerializer(serializers.ModelSerializer):
    """Сокращенное представление рецепта."""
    image = Base64ImageField(required=True)

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscriptionSerializer(UserProfileSerializer):
    """Расширяет UserSerializer полями recipes и recipes_count."""
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta(UserProfileSerializer.Meta):
        fields = [*UserProfileSerializer.Meta.fields,
                  'recipes',
                  'recipes_count',]

    def get_recipes(self, obj):
        request = self.context.get('request')
        recipes = obj.recipes.all()

        recipes_limit = request.query_params.get('recipes_limit')
        if recipes_limit:
            recipes_limit = int(recipes_limit)
            paginator = Paginator(recipes, recipes_limit)
            recipes = paginator.page(1).object_list

        return ShortRecipeSerializer(recipes,
                                     many=True,
                                     context=self.context).data

    def get_recipes_count(self, obj):
        return obj.recipes.count()
