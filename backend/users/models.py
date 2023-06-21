from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    email = models.EmailField(
        verbose_name='Электронная почта',
        max_length=254,
        unique=True
    )
    username = models.CharField(
        verbose_name='Логин пользователя',
        max_length=150,
        unique=True
    )
    first_name = models.CharField(
        verbose_name='Имя пользователя',
        max_length=150
    )
    last_name = models.CharField(
        verbose_name='Фамилия пользователя',
        max_length=150
    )

    USERNAME_FIELD = 'email'

    REQUIRED_FIELDS = ('username',
                       'first_name',
                       'last_name',)

    class Meta():
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        constraints = [
            models.CheckConstraint(
                check=~models.Q(username__iexact='me'),
                name='username_cannot_be_me'
            )
        ]

    def __str__(self) -> str:
        return self.username


class Subscription(models.Model):
    follower = models.ForeignKey(
        User,
        verbose_name='Подписчик',
        related_name='follower',
        on_delete=models.CASCADE
    )
    following = models.ForeignKey(
        User,
        verbose_name='Подписка',
        related_name='following',
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
