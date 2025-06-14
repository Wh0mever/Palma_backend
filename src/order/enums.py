from django.db import models


class OrderStatus(models.TextChoices):
    CREATED = 'CREATED', 'Создан'
    # ACCEPTED = 'ACCEPTED', 'Принят'
    COMPLETED = 'COMPLETED', 'Завершен'
    CANCELLED = 'CANCELLED', 'Отменен'
