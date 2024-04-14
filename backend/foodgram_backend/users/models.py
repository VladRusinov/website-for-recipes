from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models

from users.constants import EMAIL_MAX_LENGTH, LETTER_LIMIT, MAX_LENGTH


class User(AbstractUser):
    """Модель пользователя."""

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name', 'password']

    username = models.CharField(
        'Имя пользователя',
        max_length=MAX_LENGTH,
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^[\w.@+-]+\Z',
                message='Имя пользователя может содержать'
                        'только буквы, цифры и @/./+/-/_.'
            )
        ]
    )
    first_name = models.CharField('Имя', max_length=MAX_LENGTH)
    last_name = models.CharField('Фамилия', max_length=MAX_LENGTH)
    email = models.EmailField(
        'Адрес электронной почты', unique=True, max_length=EMAIL_MAX_LENGTH
    )
    password = models.CharField('Пароль', max_length=MAX_LENGTH)

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=~models.Q(username='me'),
                name='no_me_username'
            )
        ]
        ordering = ['id']
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username[:LETTER_LIMIT]


class Follow(models.Model):
    """Модель подписки."""

    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        on_delete=models.CASCADE,
        related_name='follow',
    )
    following = models.ForeignKey(
        User,
        verbose_name='Подписка',
        on_delete=models.CASCADE,
        related_name='following'
    )

    class Meta:
        ordering = ['id']
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'following'], name='unique_following'
            ),
            models.CheckConstraint(
                name="%(app_label)s_%(class)s_prevent_self_follow",
                check=~models.Q(user=models.F("following")),
            ),
        ]

    def __str__(self) -> str:
        return f"{self.user} - {self.following}"[:LETTER_LIMIT]
