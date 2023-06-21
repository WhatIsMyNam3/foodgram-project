from django.contrib import admin
from recipes.models import (Ingredient, IngredientRecipe, Recipe,
                            ShoppingCart, Tag, Favorite)
from users.models import Subscription, User


class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'author',
        'name',
        'image',
        'text',
        'ingredients',
        'is_favorited',
    )
    search_fields = ('author', 'name')
    list_filter = ('author', 'name', 'tags')
    empty_value_display = '-'

    def is_favorited(self, obj):
        return obj.favorites.count()

    def ingredients(self, obj):
        return list(obj.ingredients.all())


class UserAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'username',
        'first_name',
        'last_name',
        'email',
        'password',
        'is_staff',
    )
    ordering = ('email',)
    search_fields = ('username', 'email',)


class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'measurement_unit',
    )
    search_fields = ('name', )


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(User, UserAdmin)
admin.site.register(Tag)
admin.site.register(Favorite)
admin.site.register(ShoppingCart)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(IngredientRecipe)
admin.site.register(Subscription)
