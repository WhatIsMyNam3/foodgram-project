from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import SAFE_METHODS, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from api.permissions import IsAdminOrReadOnly, IsOwnerOrIsAdminOrReadOnly
from recipes.models import (Favorite, Ingredient, IngredientRecipe, Recipe,
                            ShoppingCart, Tag)
from users.models import Subscription, User
from .filters import IngredientFilter, RecipeFilter
from .serializers import (CreateRecipeSerializer, IngredientSerializer,
                          RecipeSerializer, ShoppingCartSerializer,
                          SubscriptionSerializer, TagSerializer,
                          UserSerializer)


class UserViewSet(DjoserUserViewSet):
    """Вьюсет пользователя."""
    queryset = User.objects.all()
    pagination_class = PageNumberPagination
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, ]

    @action(
        methods=['get', ],
        detail=False,
        permission_classes=[IsAuthenticated, ]
    )
    def me(self, request):
        """Эндпоинт для получения информации о текущем пользователе."""
        serializer = UserSerializer(
            request.user,
            context={'request': request}
        )
        return Response(serializer.data)

    def add_obj(self, author, id):
        """Подписка на пользователя по id."""
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
        """Удаление подписки на пользователя по id."""
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
        """Эндпоинт для подписки на пользователя или отписки от него."""
        if request.method == 'POST':
            return self.add_obj(request.user, id)
        return self.del_obj(request.user, id)

    @action(
        methods=['get', ],
        detail=False,
        permission_classes=[IsAuthenticated, ]
    )
    def subscriptions(self, request):
        """Эндпоинт для получения списка подписок."""
        users = User.objects.filter(follower__following=request.user)
        pages = self.paginate_queryset(users)

        serializer = SubscriptionSerializer(
            pages,
            context={'request': self.request},
            many=True
        )
        return self.get_paginated_response(serializer.data)


class RecipeViewSet(ModelViewSet):
    """Вьюсет для рецепта."""
    queryset = Recipe.objects.all()
    permission_classes = (IsOwnerOrIsAdminOrReadOnly, )
    pagination_class = PageNumberPagination
    pagination_class.page_size_query_param = 'limit'
    pagination_class.page_size = 6
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        """Выбор серилизатора в зависимости от метода."""
        if self.request in SAFE_METHODS:
            return RecipeSerializer
        return CreateRecipeSerializer

    def add_obj(self, obj, user, id):
        """Добавление рецепта в список избранных или корзину."""
        if obj.objects.filter(user=user, recipe__id=id).exists():
            return Response(
                {'errors': 'Рецепт уже в списке'},
                status=status.HTTP_400_BAD_REQUEST
            )
        recipe = get_object_or_404(Recipe, id=id)
        obj.objects.create(user=user, recipe=recipe)
        serializer = ShoppingCartSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def del_obj(self, obj, user, id):
        """Удаление рецепта из списока избранных или корзины."""
        model = obj.objects.filter(user=user, recipe__id=id)
        if model.exists():
            model.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'errors': 'Рецерт отсутствует'},
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated, ],
        pagination_class=None
    )
    def shopping_cart(self, request, pk):
        """Эндпоинт для добавления рецептов или удаления их из корзины."""
        if request.method == 'POST':
            return self.add_obj(ShoppingCart, request.user, pk)
        return self.del_obj(ShoppingCart, request.user, pk)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated, ]
    )
    def favorite(self, request, pk):
        """Эндпоинт для добавления рецептов или удаления их из избранных."""
        if request.method == 'POST':
            return self.add_obj(Favorite, request.user, pk)
        return self.del_obj(Favorite, request.user, pk)

    @action(
        detail=False,
        methods=['get', ],
        permission_classes=[IsAuthenticated, ]
    )
    def download_shopping_cart(self, request):
        """Эндпоинт для скачивания ингредиентов из корзины."""
        user = request.user
        if not user.carts.exists():
            return Response(
                {'errors': 'У вас нет списка покупок'},
                status=status.HTTP_400_BAD_REQUEST
            )
        ingredients = IngredientRecipe.objects.filter(
            recipe__recipe_in_cart__user=user).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(ingredient_amount=Sum('amount'))
        result = ['Список покупок:']
        for ingredient in ingredients:
            result.append(
                f'    ·{ingredient["ingredient__name"]} — '
                f'{ingredient["ingredient_amount"]}'
                f' {ingredient["ingredient__measurement_unit"]}'
            )
        result = '\n'.join(result)
        response = HttpResponse(
            result,
            content_type='text.txt; charset=utf-8'
        )
        response['Content-Disposition'] = 'attachment; filename=ShopList.txt'
        return response


class IngredientViewSet(ModelViewSet):
    """Вьюсет для ингредиента."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (IsAdminOrReadOnly, )
    http_method_names = ['post', 'get', 'patch', 'delete']
    filter_backends = [IngredientFilter]
    search_fields = ['^name']


class TagViewSet(ModelViewSet):
    """Вьюсет для тэга."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsAdminOrReadOnly, ]
    http_method_names = ['post', 'get', 'patch', 'delete']
