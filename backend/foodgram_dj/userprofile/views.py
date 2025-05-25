# from djoser.views import UserViewSet
from rest_framework.decorators import action
from rest_framework import viewsets, pagination, mixins, permissions
from .models import UserProfile, Subscription
from .serializers import UserProfileSerializer, SubscriptionSerializer


class SubscriptionViewSet(viewsets.GenericViewSet,
                          mixins.CreateModelMixin,
                          mixins.DestroyModelMixin):
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer
    permission_classes = (permissions.IsAuthenticated, )


class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    pagination_class = pagination.LimitOffsetPagination

    # from django_filters.rest_framework import DjangoFilterBackend
    # filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    # filterset_fields = ('color', 'birth_year')
    # search_fields = ('name',)
