from django.db import models


class ProductUnitType(models.TextChoices):
    PIECE = 'PIECE', 'шт.'
    MR = 'METER', 'м.'
    CM = 'CENTIMETER', 'см.'
    BRANCH = 'BRANCH', 'ветка'
    PACKAGE = 'PACKAGE', 'Пачка'
