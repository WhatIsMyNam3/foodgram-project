from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import SAFE_METHODS, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from api.permissions import IsAdminOrReadOnly, IsOwnerOrIsAdminOrReadOnly
from recipes.models import (Favorite, Ingredient, IngredientRecipe, Recipe,
                            ShoppingCart, Tag)
from users.serializers import ShoppingCartSerializer

from .filters import RecipeFilter
from .serializers import (CreateRecipeSerializer, IngredientSerializer,
                          RecipeSerializer, TagSerializer)


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (IsOwnerOrIsAdminOrReadOnly, )
    pagination_class = LimitOffsetPagination
    filter_backends = [DjangoFilterBackend, ]
    filterset_class = RecipeFilter

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.request in SAFE_METHODS:
            return RecipeSerializer
        return CreateRecipeSerializer

    def add_obj(self, obj, user, id):
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
        permission_classes=[IsAuthenticated, ]
    )
    def shopping_cart(self, request, pk):
        if request.method == 'POST':
            return self.add_obj(ShoppingCart, request.user, pk)
        return self.del_obj(ShoppingCart, request.user, pk)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated, ]
    )
    def favorite(self, request, pk):
        if request.method == 'POST':
            return self.add_obj(Favorite, request.user, pk)
        return self.del_obj(Favorite, request.user, pk)

    @action(
        detail=False,
        methods=['get', ],
        permission_classes=[IsAuthenticated, ]
    )
    def download_shopping_cart(self, request):
        user = request.user
        if not user.carts.exists():
            return Response(
                {'errors': 'У вас нет списка покупок'},
                status=status.HTTP_400_BAD_REQUEST
            )
        ingredients = IngredientRecipe.objects.filter(
            recipe__recipe_in_cart__user=user)
        shopping_list = {}
        for ingredient in ingredients:
            amount = ingredient.amount
            name = ingredient.ingredient.name
            measurement_unit = ingredient.ingredient.measurement_unit
            if name in shopping_list:
                shopping_list[name]['amount'] += amount
            else:
                shopping_list[name] = {
                    'measurement_unit': measurement_unit,
                    'amount': amount
                }
        result = ['Список покупок:']
        print(shopping_list)
        for key, values in shopping_list.items():
            result.append(
                f'    ·{key} — {values["amount"]} {values["measurement_unit"]}'
            )
        shopping_list = '\n'.join(result)
        response = HttpResponse(
            shopping_list,
            content_type='text.txt; charset=utf-8'
        )
        response['Content-Disposition'] = 'attachment; filename=ShopList.txt'
        return response


class IngredientViewSet(ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (IsAdminOrReadOnly, )
    http_method_names = ['post', 'get', 'patch', 'delete']
    filter_backends = [SearchFilter]
    search_fields = ['^name']


class TagViewSet(ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsAdminOrReadOnly, ]
    http_method_names = ['post', 'get', 'patch', 'delete']
