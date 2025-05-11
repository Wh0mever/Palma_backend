from django.db import models
from django.contrib.auth import get_user_model
from django.db.models.functions import Coalesce
from django.utils import timezone

from src.base.models import FlagsModel
from src.payment.enums import PaymentMethods, PaymentType, PaymentModelType, OutlayType, CashierType
from src.payment.managers import CashierShiftQuerySet

User = get_user_model()


class PaymentMethodCategory(models.Model):
    name = models.CharField(
        max_length=255,
        verbose_name="Название"
    )

    class Meta:
        verbose_name = "Категория методов оплаты"
        verbose_name_plural = "Категории методов оплаты"

    def __str__(self):
        return f"{self.name}"


class PaymentMethod(models.Model):
    name = models.CharField(
        max_length=255,
        verbose_name="Название"
    )
    category = models.ForeignKey(
        "payment.PaymentMethodCategory",
        on_delete=models.PROTECT,
        related_name="payment_methods",
        verbose_name="Категория"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Активен?"
    )

    class Meta:
        verbose_name = "Метод оплаты"
        verbose_name_plural = "Методы оплаты"

    def __str__(self):
        return f"{self.name}"


class Payment(FlagsModel, models.Model):
    payment_method = models.ForeignKey(
        "payment.PaymentMethod",
        on_delete=models.PROTECT,
        null=True,
        related_name="payments",
        verbose_name="Метод оплаты"
    )
    payment_type = models.CharField(
        max_length=255,
        choices=PaymentType.choices,
        verbose_name="Доход/Расход"
    )
    payment_model_type = models.CharField(
        max_length=255,
        choices=PaymentModelType.choices,
        verbose_name="Тип оплаты"
    )
    income = models.ForeignKey(
        "income.Income",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="payments",
        verbose_name="Приход"
    )
    order = models.ForeignKey(
        "order.Order",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="payments",
        verbose_name="Заказ"
    )
    provider = models.ForeignKey(
        "income.Provider",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="payments",
        verbose_name="Поставщик"
    )
    client = models.ForeignKey(
        "order.Client",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="payments",
        verbose_name="Клиент"
    )
    outlay = models.ForeignKey(
        "payment.Outlay",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="payments",
        verbose_name="Расход"
    )
    worker = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="payments",
        verbose_name="Сотрудник"
    )
    amount = models.DecimalField(
        max_digits=19,
        decimal_places=2,
        verbose_name="Сумма"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания"
    )
    created_user = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="created_payments",
        verbose_name="Создал"
    )
    deleted_user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name="payments_deleted",
        blank=True,
        null=True,
        verbose_name="Удалил"
    )
    comment = models.TextField(
        blank=True,
        null=True,
        verbose_name="Комментарии"
    )
    is_debt = models.BooleanField(
        default=False,
        verbose_name='Оплата долга'
    )

    class Meta:
        verbose_name = "Платеж"
        verbose_name_plural = "Платежи"
        ordering = ['-created_at']

    def __str__(self):
        return f"Платеж #{self.id} | {self.amount} Сум | {self.created_at.strftime('%d.%m.%Y, %H:%M')}"


class Outlay(FlagsModel, models.Model):
    title = models.CharField(
        max_length=255,
        verbose_name="Название"
    )
    outlay_type = models.CharField(
        max_length=255,
        choices=OutlayType.choices,
        verbose_name="Тип расходов"
    )
    industry = models.ForeignKey(
        'product.Industry',
        on_delete=models.SET_NULL,
        related_name='outlays',
        null=True,
        blank=True,
        verbose_name='Отрасль'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания"
    )
    created_user = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="outlays",
        verbose_name="Создал"
    )
    comment = models.TextField(
        blank=True,
        null=True,
        verbose_name="Комментарии"
    )

    class Meta:
        verbose_name = "Причина расхода"
        verbose_name_plural = "Причины расхода"

    def __str__(self):
        return self.title


class Cashier(models.Model):
    payment_method = models.ForeignKey(
        'payment.PaymentMethod',
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="cashiers",
        verbose_name="Тип кассы"
    )
    amount = models.DecimalField(
        max_digits=19,
        decimal_places=2,
        default=0,
        verbose_name="Сумма"
    )

    class Meta:
        ordering = ['id']
        verbose_name = "Касса"
        verbose_name_plural = "Кассы"

    def __str__(self):
        return f"{self.amount} - {self.payment_method}"


class CashierShift(models.Model):
    start_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата начала"
    )
    end_date = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="Дата конца"
    )
    started_user = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='started_shifts',
        verbose_name="Открыл смену"
    )
    completed_user = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='completed_shifts',
        verbose_name="Закрыл смену"
    )
    cash_income_amount = models.DecimalField(
        max_digits=19,
        decimal_places=2,
        default=0,
        verbose_name="Сумма прихода (наличные)"
    )
    cash_outcome_amount = models.DecimalField(
        max_digits=19,
        decimal_places=2,
        default=0,
        verbose_name="Сумма расхода (наличные)"
    )
    overall_income_amount = models.DecimalField(
        max_digits=19,
        decimal_places=2,
        default=0,
        verbose_name="Сумма расхода"
    )
    overall_outcome_amount = models.DecimalField(
        max_digits=19,
        decimal_places=2,
        default=0,
        verbose_name="Сумма расхода"
    )

    objects = CashierShiftQuerySet.as_manager()

    class Meta:
        ordering = ['-start_date']
        verbose_name = "Смена кассы"
        verbose_name_plural = "Смены кассы"

    def __str__(self):
        return f"{self.start_date.strftime('%d.%m.%Y %H:%M')} - {self.started_user}"

    def get_total_profit(self):
        return self.overall_income_amount - self.overall_outcome_amount

    def get_total_profit_cash(self):
        return self.cash_income_amount - self.cash_outcome_amount
