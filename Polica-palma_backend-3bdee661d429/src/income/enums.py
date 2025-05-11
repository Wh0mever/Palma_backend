from django.db import models


class IncomeStatus(models.TextChoices):
    CREATED = "CREATED", "Создан"
    ACCEPTED = "ACCEPTED", "Принят"
    COMPLETED = "COMPLETED", "Завершен"
    CANCELLED = "CANCELLED", "Отменен"
