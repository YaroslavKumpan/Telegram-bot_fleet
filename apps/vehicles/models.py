from django.db import models
from apps.users.models import User

class Vehicle(models.Model):
    number = models.CharField(
        'Государственный номер',
        max_length=20,
        unique=True
    )
    driver = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='vehicles',
        verbose_name='Водитель'
    )

    class Meta:
        verbose_name = 'Автомобиль'
        verbose_name_plural = 'Автомобили'

    def __str__(self):
        return self.number