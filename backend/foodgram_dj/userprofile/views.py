from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import pagination, permissions, status
from djoser import views
from .models import UserProfile
from .serializers import UserProfileSerializer


class UserProfileViewSet(views.UserViewSet):
    """Представление профиля пользователя."""
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    pagination_class = pagination.LimitOffsetPagination
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, ]

    @action(detail=False,
            methods=['get'],
            url_path='me',
            permission_classes=[permissions.IsAuthenticated])
    def get_current_user(self, request):
        """Метод для получения текущего пользователя"""
        return Response(self.get_serializer(request.user).data)

    @action(detail=True, methods=['get'])
    def get_user(self, request, pk=None):
        """Получение страницы пользователя."""
        user = self.get_object()
        if not user:
            return Response({'detail': 'Страница не найдена.'},
                            status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(user)
        data = serializer.data
        return Response(data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['put', 'delete'], url_path='me/avatar')
    def put_delete_avatar(self, request):
        """Создать или удалить аватар."""
        user = request.user

        if request.method == 'PUT':
            if 'avatar' not in request.data:
                return Response(
                    {'detail': 'Поле "avatar" не задано!'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            serializer = self.get_serializer(user,
                                             data=request.data,
                                             partial=True)
            serializer.is_valid(raise_exception=True)

            if user.avatar:
                user.avatar.delete(save=True)

            serializer.save()
            return Response(
                {'avatar': serializer.data['avatar']},
                status=status.HTTP_200_OK
            )
        # DELETE запрос
        elif request.method == 'DELETE':
            if not user.avatar:
                return Response(
                    {'detail': 'Аватар не существует!'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            user.avatar.delete(save=True)
            user.save()
            return Response(
                {'message': 'Аватар успешно удалён'},
                status=status.HTTP_204_NO_CONTENT
            )
