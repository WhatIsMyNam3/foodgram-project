from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Subscription, User
from .serializers import SubscriptionSerializer, UserSerializer


class UserViewSet(DjoserUserViewSet):
    queryset = User.objects.all()
    pagination_class = LimitOffsetPagination
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, ]

    @action(
        methods=['get', ],
        detail=False,
        permission_classes=[IsAuthenticated, ]
    )
    def me(self, request):
        serializer = UserSerializer(
            request.user,
            context={'request': request}
        )
        return Response(serializer.data)

    def add_obj(self, author, id):
        queryset = Subscription.objects.filter(
            following=author,
            follower__id=id
        )
        if queryset.exists():
            return Response(
                {'errors': 'Вы уже подписаны на этого пользователя'},
                status=status.HTTP_400_BAD_REQUEST
            )
        follower = get_object_or_404(User, id=id)
        if follower == author:
            return Response(
                {'errors': 'Подписываться на себя нельзя'},
                status=status.HTTP_400_BAD_REQUEST
            )
        Subscription.objects.create(
            following=author,
            follower=follower
        )
        serializer = SubscriptionSerializer(
            follower,
            context={'request': self.request}
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def del_obj(self, user, id):
        model = Subscription.objects.filter(following=user, follower__id=id)
        if model.exists():
            model.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'errors': 'Рецерт отсутствует'},
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(
        methods=['post', 'delete'],
        detail=True,
        permission_classes=[IsAuthenticated, ]
    )
    def subscribe(self, request, id):
        if request.method == 'POST':
            return self.add_obj(request.user, id)
        return self.del_obj(request.user, id)

    @action(
        methods=['get', ],
        detail=False,
        permission_classes=[IsAuthenticated, ]
    )
    def subscriptions(self, request):
        subscriptions = Subscription.objects.filter(following=request.user)
        if not subscriptions.exists():
            return Response(status=status.HTTP_204_NO_CONTENT)
        user = []
        for i in subscriptions:
            user.append(i.follower)
        serializer = SubscriptionSerializer(
            user,
            context={'request': self.request},
            many=True
        )
        return Response(serializer.data)
