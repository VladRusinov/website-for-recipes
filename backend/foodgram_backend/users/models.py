from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models


LETTER_LIMIT = 25


class User(AbstractUser):
    """Модель пользователя."""

    USER = 'user'
    ADMIN = 'admin'
    CHOICES = (
        (USER, 'Пользователь'),
        (ADMIN, 'Админ'),
    )

    username = models.CharField(
        'Имя пользователя',
        max_length=150,
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^[\w.@+-]+\Z',
                message='Имя пользователя может содержать'
                        'только буквы, цифры и @/./+/-/_.'
            )
        ]
    )
    first_name = models.CharField('Имя', max_length=150)
    last_name = models.CharField('Фамилия', max_length=150)
    email = models.EmailField(
        'Адрес электронной почты', unique=True, max_length=254
    )
    password = models.CharField('Пароль', max_length=150)
    role = models.CharField(
        max_length=15,
        choices=CHOICES,
        default=USER,
        verbose_name='Права доступа'
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name', 'password']

    def __str__(self):
        return self.username[:LETTER_LIMIT]

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'


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

    def __str__(self) -> str:
        return f"{self.user} - {self.following}"[:LETTER_LIMIT]

    class Meta:
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
