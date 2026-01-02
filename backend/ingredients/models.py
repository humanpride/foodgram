from django.db import models
from django.db.models.functions import Lower


class Ingredient(models.Model):
    MEASUREMENT_UNITS = (
        ('граммы', 'г'),
        ('милилитры', 'мл'),
        ('штуки', 'шт.'),
        ('столовые ложки', 'ст.л.'),
        ('чайные ложки', 'ч.л.'),
    )

    name = models.CharField(max_length=128)
    measurement_unit = models.CharField(
        max_length=64, choices=MEASUREMENT_UNITS
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        indexes = [
            models.Index(Lower('name'), name='ingredient_name_idx'),
        ]
        ordering = ['name']

    def __str__(self):
        return f'{self.name} ({self.measurement_unit})'
