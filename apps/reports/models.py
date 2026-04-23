from django.db import models
from apps.vehicles.models import Vehicle

class WashReport(models.Model):
    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.CASCADE,
        related_name='wash_reports',
        verbose_name='Автомобиль'
    )
    photo = models.ImageField(
        'Фото',
        upload_to='wash_photos/'
    )
    created_at = models.DateTimeField(
        'Дата создания',
        auto_now_add=True
    )

    class Meta:
        verbose_name = 'Отчёт о мойке'
        verbose_name_plural = 'Отчёты о мойке'
        ordering = ['-created_at']

    def __str__(self):
        return f'Мойка {self.vehicle.number} от {self.created_at:%d.%m.%Y}'

class ServiceReport(models.Model):
    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.CASCADE,
        related_name='service_reports',
        verbose_name='Автомобиль'
    )
    photo = models.ImageField(
        'Фото акта',
        upload_to='service_photos/'
    )
    created_at = models.DateTimeField(
        'Дата создания',
        auto_now_add=True
    )

    class Meta:
        verbose_name = 'Акт выполненных работ'
        verbose_name_plural = 'Акты выполненных работ'
        ordering = ['-created_at']

    def __str__(self):
        return f'Акт {self.vehicle.number} от {self.created_at:%d.%m.%Y}'