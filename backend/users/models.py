from django.contrib.auth.models import AbstractUser
from django.db import models
from recipes.validators import validate_username


class User(AbstractUser):
    """Модель пользователя."""

    username = models.CharField(
        'Никнейм',
        max_length=150,
        unique=True,
        validators=[validate_username,]
    )
    first_name = models.CharField(
        'Имя',
        max_length=150,
    )
    last_name = models.CharField(
        'Фамилия',
        max_length=150,
    )
    email = models.EmailField(
        'Электронная почта',
        unique=True,
    )
    password = models.CharField(
        'Пароль',
        max_length=150,
        blank=False,
        null=False
    )
    avatar = models.ImageField(
        upload_to='avatars/',
        blank=True,
        null=True
    )

    class Meta:
        ordering = ('username',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


class Follow(models.Model):
    """Подписка"""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор',
    )

    class Meta:
        ordering = ('author',)
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'author'),
                name='unique_user_author'
            )
        ]

    def __str__(self):
        return f'{self.user} подписан на {self.author}'
