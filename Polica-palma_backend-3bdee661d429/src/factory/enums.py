from django.db import models


class ProductFactoryStatus(models.TextChoices):
    CREATED = "CREATED", "Создан"
    FINISHED = "FINISHED", "Завершен"
    SOLD = "SOLD", "Продан"
    PENDING = "PENDING", "В ожидании разборки"
    # CANCELLED = "CANCELLED", "Отменен"
    WRITTEN_OFF = "WRITTEN_OFF", "Списан"


class ProductFactorySalesType(models.TextChoices):
    STORE = "STORE", "Магазин"
    SHOWCASE = "SHOWCASE", "Витрина"
    CONGRATULATION = "CONGRATULATION", "Поздравление"


class FactoryTakeApartRequestType(models.TextChoices):
    TO_CREATE = "TO_CREATE", "Разборка"
    WRITE_OFF = "WRITE_OFF", "Списание"
