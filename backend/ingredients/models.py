from django.db import models
from django.db.models.functions import Lower


class Ingredient(models.Model):
    name = models.CharField('Название', max_length=128)
    measurement_unit = models.CharField(
        'Единица измерения',
        max_length=64,
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
