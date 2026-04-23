import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    class Role(models.TextChoices):
        DRIVER = 'driver', 'Водитель'
        ACCOUNTANT = 'accountant', 'Бухгалтер'
        DIRECTOR = 'director', 'Директор'

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.DRIVER,
        verbose_name='Роль'
    )
    telegram_id = models.BigIntegerField(
        unique=True,
        null=True,
        blank=True,
        verbose_name='Telegram ID'
    )
    invite_code = models.UUIDField(
        unique=True,
        null=True,
        blank=True,
        verbose_name='Код приглашения'
    )

    # Убираем обязательность email
    email = models.EmailField(blank=True, null=True)

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        if self.first_name and self.last_name:
            return f'{self.first_name} {self.last_name}'
        return self.username

    @property
    def full_name(self):
        return self.__str__()