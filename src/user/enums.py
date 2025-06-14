from django.db import models


class UserType(models.TextChoices):
    ADMIN = "ADMIN", "Админ"
    SALESMAN = "SALESMAN", "Продавец"
    FLORIST = "FLORIST", "Флорист с фиксированной платой"
    FLORIST_PERCENT = "FLORIST_PERCENT", "Флорист с процентной платой"
    MANAGER = "MANAGER", "Менеджер"
    WAREHOUSE_MASTER = "WAREHOUSE_MASTER", "Зав. склад"
    CRAFTER = "CRAFTER", "Собиратель",
    NO_BONUS_SALESMAN = "NO_BONUS_SALESMAN", "Продавец без зарплаты"
    CASHIER = "CASHIER", "Кассир"
    FLORIST_ASSISTANT = "FLORIST_ASSISTANT", "Помощник флориста"
    INCOME_MANAGER = "INCOME_MANAGER", "Закупщик"
    OTHER = "OTHER", "Прочие сотрудники"


class WorkerIncomeReason(models.TextChoices):
    PRODUCT_SALE = "PRODUCT_SALE", "Совершил/а продажу"
    PRODUCT_FACTORY_SALE = "PRODUCT_FACTORY_SALE", "Продался букет"
    PRODUCT_FACTORY_CREATE = "PRODUCT_FACTORY_CREATE", "Создание букета"
    # BONUS = "BONUS", "Премия"
    # SALARY = "SALARY", "Зарплата"
    # FINE = "FINE", "Штраф"


class WorkerIncomeType(models.TextChoices):
    INCOME = "INCOME", "Доход"
    OUTCOME = "OUTCOME", "Расход"
