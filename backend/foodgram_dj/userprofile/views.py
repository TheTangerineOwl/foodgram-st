# from djoser.views import UserViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets, pagination, mixins, permissions, status
from djoser import views
from .models import UserProfile, Subscription
from .serializers import UserProfileSerializer, SubscriptionSerializer


class SubscriptionViewSet(viewsets.GenericViewSet,
                          mixins.CreateModelMixin,
                          mixins.DestroyModelMixin):
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer
    permission_classes = (permissions.IsAuthenticated, )


class UserProfileViewSet(views.UserViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    pagination_class = pagination.LimitOffsetPagination
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, ]

    @action(detail=False, methods=['get'], url_path='me')
    def get_current_user(self, request):
        """Метод для получения текущего пользователя"""
        return Response(self.get_serializer(request.user).data)

    @action(detail=True, methods=['get'])
    def get_user(self, request, pk=None):
        # user = get_object_or_404(UserProfile, pk=pk)
        user = self.get_object()
        # is_subscribed = Subscription.objects.filter(
        #     follows=user.pk,
        #     user=request.user.pk
        # ).exists()
        serializer = self.get_serializer(user)
        data = serializer.data
        # data['is_subscribed'] = is_subscribed
        return Response(data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['put', 'delete'], url_path='me/avatar')
    def put_delete_avatar(self, request):
        user = request.user
        if request.method == 'PUT':
            serializer = self.get_serializer(user,
                                             data=request.data,
                                             partial=True)
            serializer.is_valid(raise_exception=True)

            if user.avatar:
                user.avatar.delete()

            serializer.save()
            return Response(
                {'avatar': serializer.data['avatar']},
                status=status.HTTP_200_OK
            )
        user.avatar.delete()
        user.save()
        return Response(
            {'message': 'Аватар успешно удалён'},
            status=status.HTTP_204_NO_CONTENT
        )
