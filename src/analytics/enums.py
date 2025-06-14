from django.db import models


class ProductAnalyticsIndicator(models.TextChoices):
    TURNOVER_SUM = "TURNOVER_SUM", "Сумма оборота"
    TURNOVER_PERCENT = "TURNOVER_PERCENT", "Процент от оборота"
    PROFIT_SUM = "PROFIT_SUM", "Сумма прибыли"
    PROFIT_PERCENT = "PROFIT_PERCENT", "Процент от прибыли"
    SALE_COUNT = "SALE_COUNT", "Кол-во продаж"
    WRITE_OFF_COUNT = "WRITE_OFF_COUNT", "Кол-во списаний"
    WRITE_OFF_SUM = "WRITE_OFF_SUM", "Сумма списаний"


class FloristsAnalyticsIndicator(models.TextChoices):
    FINISHED_PRODUCTS = "FINISHED_PRODUCTS", "Кол-во собранных букетов"
    SOLD_PRODUCTS = "SOLD_PRODUCTS", "Кол-во проданных букетов"
    SALES_AMOUNT = "SALES_AMOUNT", "Сумма продаж букетов"
    SALES_PROFIT_AMOUNT = "SALES_PROFIT_AMOUNT", "Сумма прибыли с продаж букетов"


class SalesmenAnalyticsIndicator(models.TextChoices):
    SALES_COUNT = "SALES_COUNT", "Кол-во продаж"
    PRODUCT_SALES_COUNT = "PRODUCT_SALES_COUNT", "Кол-во проданных товаров"
    SALES_AMOUNT = "SALES_AMOUNT", "Сумма продаж"
    SALES_PROFIT_AMOUNT = "SALES_PROFIT_AMOUNT", "Сумма прибыли с продаж"


class OutlaysAnalyticsIndicator(models.TextChoices):
    OUTCOME = "OUTCOME", "Денежные расходы"
    INCOME = "INCOME", "Денежные приходы"


class ClientsAnalyticsIndicator(models.TextChoices):
    DEBT = "debt", "Долг"
    TOTAL_ORDERS_SUM = "total_orders_sum", "Сумма покупок"
    ORDERS_COUNT = "orders_count", "Кол-во покупок"
