"""Сериализаторы для моделей рецептов и ингредиентов."""
from base64 import b64decode
from io import StringIO
from django.contrib.auth import get_user
from django.core.files.base import ContentFile
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _
from django_short_url.models import ShortURL
from django_short_url.views import get_surl
# from django_short_url.urls import
from rest_framework import serializers, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Recipe, Ingredient, IngredientRecipe, ShoppingCart


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
        fields = '__all__'


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
        obj.is_in_shopping_cart = False

        return obj.is_in_shopping_cart

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

        short_url, created = ShortURL.objects.get_or_create(url=full_url)
        # Возвращаем короткую ссылку
        return Response({
            'short-link': short_url
        }, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post', 'delete'], url_path='shopping_cart')
    def post_delete_shopping_cart(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)

        user = get_user(request=request)

        if request.method == 'POST':
            note, created = ShoppingCart.objects.get_or_create(
                user=user, recipe=recipe)
            if not created:
                return Response(detail='Рецепт уже в списке покупок!',
                                status=status.HTTP_400_BAD_REQUEST)
            return Response(status=status.HTTP_201_CREATED)
        elif request.method == 'DELETE':
            count, var = ShoppingCart.objects.filter(
                user=user, recipe=recipe).delete()
            if count == 0:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], url_path='download-shopping-cart')
    def download_cart(self, request):
        user = get_user(request=request)

        ingredients = {}

        pk_in_cart = ShoppingCart.objects.filter(user=user)
        for recipe_pk in pk_in_cart:
            in_recipe = Recipe.objects.get(pk=recipe_pk).ingredients
            for ingr in in_recipe:
                product = Ingredient.objects.get(pk=ingr.pk)
                if product in ingredients.keys:
                    ingredients[product] += ingr.amount
                else:
                    ingredients[product] = ingr.amount

        if len(ingredients) == 0:
            return Response(detail='Список покупок пуст!',
                            status=status.HTTP_200_OK)

        # file = open('shoppingcart.txt', 'w')
        file = StringIO()
        for ingredient, amount in ingredients:
            s = f'{ingredient.name} - {amount} {ingredient.measurement_unit}\n'
            file.write(s)

        return FileResponse(file, as_attachment=True,
                            filename='shoppingcart.txt')
