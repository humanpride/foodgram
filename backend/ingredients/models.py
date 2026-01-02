from django.db import models


class Ingredient(models.Model):
    MEASUREMENT_UNITS = (
        ('граммы', 'г'),
        ('милилитры', 'мл'),
        ('штуки', 'шт.'),
        ('столовые ложки', 'ст.л.'),
        ('чайные ложки', 'ч.л.'),
    )

    name = models.CharField(
        'Название',
        max_length=20,
    )
    measurement_unit = models.CharField(
        'Единица измерения',
        max_length=10,
        choices=MEASUREMENT_UNITS,
    )
