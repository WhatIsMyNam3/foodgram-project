from drf_extra_fields.fields import Base64ImageField
from djoser.serializers import UserSerializer
from rest_framework.serializers import SerializerMethodField, ModelSerializer

from .models import Subscription, User
from recipes.models import Recipe


class UserSerializer(UserSerializer):
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
            'is_subscribed'
        ]

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        return Subscription.objects.filter(
            following=request.user,
            follower=obj).exists()

class ShoppingCartSerializer(ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time',
        )

class SubscriptionSerializer(UserSerializer):
    """Серилизатор подписок."""
    is_subscribed = SerializerMethodField(
        read_only=True,
        default=False
    )
    recipes = ShoppingCartSerializer(
        many=True,
        read_only=True
    )
    recipes_count = SerializerMethodField(
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
            'recipes',
            'recipes_count'
        ]

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        return Subscription.objects.filter(
            following=request.user,
            follower=obj).exists()

    def get_recipes_count(self, obj):
        return obj.recipes.count()
