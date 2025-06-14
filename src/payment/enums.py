from django.db import models


class PaymentType(models.TextChoices):
    INCOME = 'INCOME', 'Доход'
    OUTCOME = 'OUTCOME', 'Расход'


class PaymentMethods(models.TextChoices):
    CASH = 'CASH', 'Наличными'
    CARD = 'CARD', 'Картой'
    TRANSFER = 'TRANSFER', 'Перечисление'
    TRANSFER_TO_CARD = 'TRANSFER_TO_CARD', 'Перевод на карту'


class PaymentModelType(models.TextChoices):
    OUTLAY = 'OUTLAY', 'Расходы'
    ORDER = 'ORDER', 'Заказ'
    INCOME = 'INCOME', 'Приход'
    PROVIDER = 'PROVIDER', 'Поставщик'


class OutlayType(models.TextChoices):
    INVESTMENT = 'INVESTMENT', 'Инвестиция'
    SPENDING = 'SPENDING', 'Затраты'
    WORKERS = 'WORKERS', 'Сотрудники'


class CashierType(models.TextChoices):
    CASH = 'CASH', 'Наличные'
    CARD = 'CARD', 'Карта'
    BANK = 'BANK', 'Банк'
