"""Сериализаторы для моделей рецептов и ингредиентов."""
from django.core.paginator import Paginator
from django.utils.translation import gettext_lazy as _
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
    amount = serializers.IntegerField(
        min_value=1,
        error_messages={
            'min_value': 'Количество должно быть больше нуля!'
        }
    )

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

    ingredients = serializers.SerializerMethodField()

    image = Base64ImageField(required=True)
    # image_url = serializers.SerializerMethodField(
    #     'get_image_url',
    #     read_only=True,
    # )
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
        # Заменяем ingredients для чтения
        representation['ingredients'] = IngredientRecipeSerializer(
            instance.recipe_ingredients.all(), many=True
        ).data
        return representation

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

    def validate_cooking_time(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                'Время приготовления должно быть больше нуля!')
        return value

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

    # def get_image_url(self, obj):
    #     """Получение ссылки на картинку."""
    #     if obj.image:
    #         return obj.image.url
    #     return None

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        return obj.user_favs.filter(user=request.user).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        return obj.shopping_carts.filter(user=request.user).exists()

    def create(self, validated_data):
        """Создание рецепта с ингредиентами."""
        ingredients_data = validated_data.pop('ingredients', [])
        if not ingredients_data or len(ingredients_data) == 0:
            raise serializers.ValidationError(
                'Поле "Игредиенты" должно быть заполнено!'
            )

        recipe = Recipe.objects.create(**validated_data)

        self.create_ingredients(recipe=recipe,
                                ingredients_data=ingredients_data)

        return recipe

    def update(self, instance, validated_data):
        """Обновление рецепта с ингредиентами."""
        ingredients_data = validated_data.pop('ingredients', None)
        if not ingredients_data or len(ingredients_data) == 0:
            raise serializers.ValidationError(
                'Поле "Игредиенты" должно быть заполнено!'
            )

        # Обновляем основные поля рецепта
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Обновляем ингредиенты, если они переданы
        if ingredients_data is not None:
            self.update_ingredients(instance, ingredients_data)

        return instance

    def create_ingredients(self, recipe, ingredients_data):
        """Создание связей с ингредиентами."""
        # Получаем все нужные ингредиенты одним запросом
        ingredient_ids = [item['id'] for item in ingredients_data]
        # Проверить надо, что они возвращаются
        ingredients = Ingredient.objects.in_bulk(ingredient_ids)
        if len(ingredients) != len(ingredient_ids):
            raise serializers.ValidationError(
                'Ингредиент не существует!'
            )
        
        ingredient_recipe_objects = []
        for ingredient_data in ingredients_data:
            if ingredient_data['id'] in ingredients:

                if int(ingredient_data['amount']) <= 0:
                    raise serializers.ValidationError(
                        'Количество не может быть меньше 1!'
                    )

                IngredientRecipe(
                    recipe=recipe,
                    ingredient=ingredients[ingredient_data['id']],
                    amount=ingredient_data['amount']
                )
        IngredientRecipe.objects.bulk_create(ingredient_recipe_objects)

    def update_ingredients(self, recipe, ingredients_data):
        """Обновление связей с ингредиентами."""
        # Удаляем старые ингредиенты
        recipe.recipe_ingredients.all().delete()
        # Создаем новые
        self.create_ingredients(recipe, ingredients_data)


class ShortRecipeSerializer(serializers.ModelSerializer):
    # id, name, image, image_url, cooking_time
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
        recipes = obj.recipes.all()  # Рецепты пользователя (follows)

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
