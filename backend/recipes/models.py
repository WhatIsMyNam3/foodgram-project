from django.core.validators import MinValueValidator, RegexValidator
from django.db import models

from users.models import User


class Tag(models.Model):
    """Модель для тэгов."""
    name = models.CharField(
        verbose_name='Тэг',
        unique=True,
        max_length=200,
    )
    color = models.CharField(
        verbose_name='Цвет тэга',
        unique=True,
        max_length=7,
        validators=(
            RegexValidator(
                regex=r'^#([A-Fa-f0-9]{6})$',
            ),
        )
    )
    slug = models.SlugField(
        verbose_name='Слаг тэга',
        unique=True,
        max_length=200,
    )

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'


class Ingredient(models.Model):
    """Модель для ингредиентов."""
    name = models.CharField(
        verbose_name='Название ингредиента',
        max_length=200,
        null=False,
        validators=(
            RegexValidator(
                regex=r'([a-zA-Zа-яА-ЯёЁ]{3,})',
            ),
        )
    )
    measurement_unit = models.CharField(
        verbose_name='Мера измерения',
        max_length=200,
        null=False
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def clean(self):
        self.name = self.name.lower()
        self.measurement_unit = self.measurement_unit.lower()
        return super().clean()


class Recipe(models.Model):
    """Модель для рецептов."""
    author = models.ForeignKey(
        User,
        related_name='recipes',
        verbose_name='Автор рецепта',
        on_delete=models.CASCADE
    )
    name = models.CharField(
        verbose_name='Название рецепта',
        max_length=200
    )
    text = models.TextField(
        verbose_name='Описание рецепта',
    )
    cooking_time = models.PositiveIntegerField(
        verbose_name='Время приготовления',
        default=1,
        validators=[
            MinValueValidator(
                1,
                message='Минимальное время - 1 минута'
            ),
        ],
    )
    image = models.ImageField(
        verbose_name='Картинка итогового блюда',
        upload_to='recipes/images/',
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Тэги',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        related_name='recipes',
        verbose_name='Ингредиенты',
        through='IngredientRecipe'
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True,
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ['-pub_date']


class IngredientRecipe(models.Model):
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredient',
        verbose_name='Ингредиент',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe',
        verbose_name='Рецепт',
    )
    amount = models.PositiveSmallIntegerField(
        default=1,
        verbose_name='Количество ингредиентов',
    )

    class Meta:
        verbose_name = 'Количество'
        constraints = [
            models.UniqueConstraint(
                fields=['ingredient', 'recipe'],
                name='ingredient_amount_unique')
        ]


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        related_name='carts',
        verbose_name='Пользователь',
        on_delete=models.CASCADE
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_in_cart',
        verbose_name='Рецепт',
    )

    class Meta:
        verbose_name = 'Рецепт в списке покупок'
        verbose_name_plural = 'Рецепты в списке покупок'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='shopping_cart_unique')
        ]


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        related_name='favorites',
        verbose_name='Пользователь',
        on_delete=models.CASCADE
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Рецепт',
    )

    class Meta:
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='favorute_unique')
        ]
