from django.db import models


class FactoryType(models.TextChoices):
    FLOWERS = 'FLOWERS', 'Цветочный'
    SWEETS = 'SWEETS', 'Сладкий'
