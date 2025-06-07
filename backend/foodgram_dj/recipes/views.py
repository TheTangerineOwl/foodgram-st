"""Представления для приложения dishes."""
from io import BytesIO
from django.db.models import Sum
from django.http import FileResponse
from django.contrib.auth import get_user
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, permissions, filters, status
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import action
from rest_framework.response import Response
from django_short_url.models import ShortURL
from django_short_url.views import get_surl
from django_filters.rest_framework import DjangoFilterBackend
from .models import (Recipe, Ingredient, ShoppingCart,
                     IngredientRecipe, Favorites)
from .serializers import (IngredientSerializer,
                          RecipeSerializer)
from .permissions import AuthorOrReadOnly
from .filters import RecipeFilter


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Представление для получения одного ингредиента или списка по поиску."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    filterset_fields = ('name', )
    search_fields = ('^name', )

    def get_queryset(self):
        """Метод для получения ингредиентов по имени"""
        name = self.request.query_params.get('name')
        if name:
            return self.queryset.filter(name__istartswith=name.lower())
        return self.queryset


class RecipeViewSet(viewsets.ModelViewSet):
    """Представление для получения рецепта."""
    queryset = Recipe.objects.all().order_by('created_at')
    serializer_class = RecipeSerializer
    pagination_class = PageNumberPagination
    permission_classes = (AuthorOrReadOnly,)
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    search_fields = ('name',)
    filterset_fields = ('name', )
    filterset_class = RecipeFilter

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=['get'], url_path='get-link')
    def get_short_link(self, request, pk=None):
        # recipe = get_object_or_404(Recipe, pk=pk)
        recipe = self.get_object()

        # Создаем полный URL для рецепта
        full_url = request.build_absolute_uri(recipe.get_absolute_url())

        short_url, created = ShortURL.objects.get_or_create(lurl=full_url)

        if created or not short_url.surl:
            short_url.surl = get_surl(short_url.id)  # Генерируем короткий URL
            short_url.save()

        if not short_url.surl:
            return Response({'error': 'Short URL generation failed'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        scheme = 'https' if request.is_secure() else 'http'
        domain = request.get_host()
        short_link = request.build_absolute_uri(
            f'{scheme}://{domain}{short_url.surl}')

        return Response({
            'short-link': short_link
        }, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post', 'delete'], url_path='shopping_cart')
    def post_delete_shopping_cart(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)

        user = get_user(request=request)

        if request.method == 'POST':
            note, created = ShoppingCart.objects.get_or_create(
                user=user, recipe=recipe)
            if not created:
                return Response({
                                'message': 'Рецепт уже в списке покупок!',
                                'data': []
                                }, status=status.HTTP_400_BAD_REQUEST)
            # recipe.is_in_shopping_cart = True
            recipe.save()
            serializer = RecipeSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        elif request.method == 'DELETE':
            count, var = ShoppingCart.objects.filter(
                user=user, recipe=recipe).delete()
            if count == 0:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            # recipe.is_in_shopping_cart = False
            recipe.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], url_path='download_shopping_cart')
    def download_cart(self, request):
        user = request.user

        # Получаем все ингредиенты из корзины с суммированием количества
        cart_items = IngredientRecipe.objects.filter(
            recipe__shopping_carts__user=user
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(
            total_amount=Sum('amount')
        ).order_by('ingredient__name')

        if not cart_items.exists():
            return Response({
                'message': 'Ваша корзина покупок пуста',
                'status': 'success'
            }, status=status.HTTP_200_OK)

        # Формируем текстовый файл
        file_content = BytesIO()

        line = ''

        for item in cart_items:
            line += (
                f"{item['ingredient__name']} - "
                f"{item['total_amount']} "
                f"{item['ingredient__measurement_unit']}\n"
            )
        # file_content.write(line.encode('utf-8'))
        file_content.write(line.encode('utf-8'))

        # Подготавливаем файл для скачивания
        file_content.seek(0)
        response = FileResponse(
            file_content,
            content_type='text/plain',
            as_attachment=True,
            filename='shopping_list.txt'
        )

        return response

    @action(detail=True, methods=['post', 'delete'], url_path='favorite')
    def post_delete_favorite(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)

        user = get_user(request=request)

        if request.method == 'POST':
            note, created = Favorites.objects.get_or_create(
                user=user, recipe=recipe)
            if not created:
                return Response({
                                'message': 'Рецепт уже в списке Избранного!',
                                'data': []
                                }, status=status.HTTP_400_BAD_REQUEST)
            # recipe.is_favorited = True
            recipe.save()
            serializer = RecipeSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        elif request.method == 'DELETE':
            count, var = Favorites.objects.filter(
                user=user, recipe=recipe).delete()
            if count == 0:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            # recipe.is_favorited = False
            recipe.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
