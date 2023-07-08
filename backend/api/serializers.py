from djoser.serializers import UserSerializer as DjoserUserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework.serializers import (CharField, IntegerField,
                                        ModelSerializer,
                                        PrimaryKeyRelatedField,
                                        SerializerMethodField, ValidationError)

from recipes.models import (Favorite, Ingredient, IngredientRecipe, Recipe,
                            ShoppingCart, Tag)
from users.models import Subscription, User


class UserSerializer(DjoserUserSerializer):
    """Серилизатор пользователя."""
    is_subscribed = SerializerMethodField(
        read_only=True,
        default=False
    )

    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'password'
        ]
        extra_kwargs = {
            'password': {
                'write_only': True,
                'required': True},
            'is_subscribed': {
                'read_only': True}}

    def create(self, validated_data):
        user = User(
            email=validated_data['email'],
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        return Subscription.objects.filter(
            following=request.user,
            follower=obj).exists()


class TagSerializer(ModelSerializer):
    """Серилизатор тэга."""
    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(ModelSerializer):
    """Серилизатор ингредиента."""
    class Meta:
        model = Ingredient
        fields = '__all__'


class IngredientRecipeSerializer(ModelSerializer):
    """Серилизатор для меры измерения ингредиента."""
    id = PrimaryKeyRelatedField(
        source='ingredient.id',
        read_only=True
    )
    name = CharField(
        source='ingredient.name',
        read_only=True
    )
    measurement_unit = CharField(
        source='ingredient.measurement_unit',
        read_only=True
    )

    class Meta:
        model = IngredientRecipe
        fields = ['id', 'name', 'measurement_unit', 'amount']


class IngredientAmountSerializer(ModelSerializer):
    """Серилизатор для добавления количества ингредиента."""
    id = PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = IntegerField()

    class Meta:
        model = IngredientRecipe
        fields = ['id', 'amount']


class RecipeSerializer(ModelSerializer):
    """Серилизатор вывода рецепта."""
    tags = TagSerializer(
        read_only=True,
        many=True
    )
    ingredients = IngredientRecipeSerializer(
        source='recipe',
        many=True,
        read_only=True
    )
    author = UserSerializer(
        read_only=True
    )
    is_favorited = SerializerMethodField(
        read_only=True,
        default=False
    )
    is_in_shopping_cart = SerializerMethodField(
        read_only=True,
        default=False
    )

    class Meta:
        model = Recipe
        fields = '__all__'

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        return Favorite.objects.filter(user=request.user, recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(
            user=request.user,
            recipe=obj).exists()


class ShoppingCartSerializer(ModelSerializer):
    """Серилизатор корзины."""
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time',
        )


class CreateRecipeSerializer(ModelSerializer):
    """Серилизатор создания рецепта."""
    tags = PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    author = UserSerializer(read_only=True)
    ingredients = IngredientAmountSerializer(many=True)
    image = Base64ImageField()
    cooking_time = IntegerField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def validate_ingredients(self, data):
        all_ingredients = []
        for ingredient in data:
            if int(ingredient['amount']) < 1:
                raise ValidationError(
                    {'amount': 'Количество должно быть больше 0'}
                )
            if ingredient['id'] in all_ingredients:
                raise ValidationError(
                    {'ingredient': 'Ингредиенты должны быть уникальными'}
                )
            all_ingredients.append(ingredient['id'])
        if not all_ingredients:
            raise ValidationError(
                {'ingredient': 'Требуется хотя бы 1 ингредиент'}
            )
        return data

    def validate_tags(self, data):
        if not data:
            raise ValidationError(
                {'tags': 'Требуется хотя бы 1 тэг'}
            )
        return data

    def validate_cooking_time(self, data):
        if data < 1:
            raise ValidationError(
                {'cooking_time': 'Время готовки должно быть больше 0'}
            )
        return data

    def create_ingredients(self, ingredients, recipe):
        IngredientRecipe.objects.bulk_create([IngredientRecipe(
            ingredient=ingredient['id'],
            recipe=recipe,
            amount=ingredient['amount']
        ) for ingredient in ingredients])

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.create_ingredients(
            recipe=recipe,
            ingredients=ingredients
        )
        return recipe

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        instance = super().update(instance, validated_data)
        instance.tags.clear()
        instance.tags.set(tags)
        instance.ingredients.clear()
        self.create_ingredients(
            recipe=instance,
            ingredients=ingredients
        )
        return instance

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return RecipeSerializer(
            instance,
            context=context).data


class SubscriptionSerializer(UserSerializer):
    """Серилизатор подписок."""
    recipes = ShoppingCartSerializer(
        many=True,
        read_only=True
    )
    recipes_count = SerializerMethodField(
        read_only=True
    )

    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count'
        ]

    def get_recipes_count(self, obj):
        return obj.recipes.count()
