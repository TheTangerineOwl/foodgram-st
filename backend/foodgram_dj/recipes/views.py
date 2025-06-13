"""Представления для приложения dishes."""
from io import BytesIO
from django.db.models import Sum
from django.http import FileResponse
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import (viewsets, permissions, filters,
                            status, mixins, pagination)
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.decorators import action
from rest_framework.response import Response
from django_short_url.models import ShortURL
from django_short_url.views import get_surl
from django_filters.rest_framework import DjangoFilterBackend
from .models import (Recipe, Ingredient, ShoppingCart,
                     IngredientRecipe, Favorites)
from .serializers import (IngredientSerializer,
                          RecipeSerializer, ShortRecipeSerializer,
                          SubscriptionSerializer)
from .permissions import AuthorOrReadOnly
from .filters import RecipeFilter
from userprofile.models import Subscription


User = get_user_model()


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
    serializer_class = RecipeSerializer
    pagination_class = LimitOffsetPagination
    permission_classes = (AuthorOrReadOnly,)
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    search_fields = ('^name',)
    filterset_fields = ('name', )
    filterset_class = RecipeFilter

    def get_queryset(self):
        """Получение списка объектов."""
        return Recipe.objects.select_related('author').prefetch_related(
            'recipe_ingredients__ingredient',
            'user_favs',
            'shopping_carts'
        ).order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=['get'], url_path='get-link')
    def get_short_link(self, request, pk=None):
        """Получение короткой ссылки."""
        recipe = self.get_object()
        if not recipe:
            return Response(
                {'detail': 'Страница не найдена.'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Создаем полный URL для рецепта
        full_url = request.build_absolute_uri(recipe.get_absolute_url())

        short_url, created = ShortURL.objects.get_or_create(lurl=full_url)

        if created or not short_url.surl:
            short_url.surl = get_surl(short_url.id)  # Генерируем короткий URL
            short_url.save()

        if not short_url.surl:
            return Response({'detail':
                             'Не удалось сгенерировать короткую ссылку!'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        scheme = 'https' if request.is_secure() else 'http'
        domain = request.get_host()
        short_link = request.build_absolute_uri(
            f'{scheme}://{domain}{short_url.surl}')

        return Response({
            'short-link': short_link
        }, status=status.HTTP_200_OK)

    @action(detail=True,
            methods=['post', 'delete'],
            url_path='shopping_cart',
            permission_classes=[permissions.IsAuthenticated])
    def post_delete_shopping_cart(self, request, pk=None):
        """Добавление рецепта в Корзину или удаление."""
        recipe = get_object_or_404(Recipe, pk=pk)

        user = request.user
        if not user.is_authenticated:
            return Response(
                {'error': 'Authentication required'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        if request.method == 'POST':
            note, created = ShoppingCart.objects.get_or_create(
                user=user, recipe=recipe)
            if not created:
                return Response({
                                'detail': 'Рецепт уже в списке покупок!',
                                }, status=status.HTTP_400_BAD_REQUEST)
            recipe.save()
            serializer = ShortRecipeSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        elif request.method == 'DELETE':
            count, var = ShoppingCart.objects.filter(
                user=user, recipe=recipe).delete()
            if count == 0:
                return Response(
                    {
                        'detail': 'Рецепта не было в списке покупок!'
                    },
                    status=status.HTTP_400_BAD_REQUEST)
            recipe.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False,
            methods=['get'],
            url_path='download_shopping_cart',
            permission_classes=[permissions.IsAuthenticated])
    def download_cart(self, request):
        """Скачивание текстового файла со списком покупок."""
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

    @action(detail=True,
            methods=['post', 'delete'],
            url_path='favorite',
            permission_classes=[permissions.IsAuthenticated])
    def post_delete_favorite(self, request, pk=None):
        """Добавление рецепта в закладки или удаление."""
        recipe = get_object_or_404(Recipe, pk=pk)

        user = request.user
        if not user.is_authenticated:
            return Response(
                {'detail': 'Authentication required'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        if request.method == 'POST':
            note, created = Favorites.objects.get_or_create(
                user=user, recipe=recipe)
            if not created:
                return Response({
                                'detail': 'Рецепт уже в списке Избранного!',
                                }, status=status.HTTP_400_BAD_REQUEST)
            recipe.save()
            serializer = ShortRecipeSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        elif request.method == 'DELETE':
            count, var = Favorites.objects.filter(
                user=user, recipe=recipe).delete()
            if count == 0:
                return Response({
                    'detail': 'Рецепта не было в списке Избранного!'
                },
                    status=status.HTTP_400_BAD_REQUEST)
            recipe.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class SubscriptionViewSet(viewsets.GenericViewSet,
                          mixins.ListModelMixin):
    """Представление для подписки."""
    serializer_class = SubscriptionSerializer
    pagination_class = pagination.LimitOffsetPagination
    permission_classes = (permissions.IsAuthenticated, )

    def get_queryset(self):
        """Получение пользователя, на которого подписка."""
        return User.objects.filter(
            subbed_to__user=self.request.user
        ).prefetch_related('recipes')

    def list(self, request, *args, **kwargs):
        """
        Вывод списка пользователей, на которых оформлена подписка,
        вместе с их пагинированными рецептами.
        """
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class SingleSubscriptionViewSet(viewsets.GenericViewSet):
    """Вывод пользователя, на которого оформлена подписка."""
    queryset = User.objects.all()
    serializer_class = SubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=True, methods=['post', 'delete'], url_path='subscribe')
    def sub_and_unsub(self, request, pk=None):
        """Замена подобноого метода от UserProfile."""
        to_sub = get_object_or_404(User, pk=pk)

        if request.method == 'POST':
            if to_sub == request.user:
                return Response({'detail':
                                 'Нельзя подписаться на самого себя!'},
                                status=status.HTTP_400_BAD_REQUEST)
            sub, created = Subscription.objects.get_or_create(
                user=request.user, follows=to_sub)
            if not created:
                return Response({'detail': 'Подписка уже есть!'},
                                status=status.HTTP_400_BAD_REQUEST)
            serializer = self.get_serializer(to_sub)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        count, _ = Subscription.objects.filter(user=request.user,
                                               follows=to_sub).delete()
        if count == 0:
            return Response({'detail': 'Ошибка отписки: не был подписан!'},
                            status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_204_NO_CONTENT)
