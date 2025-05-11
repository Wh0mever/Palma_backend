from decimal import Decimal

from django.db import models
from django.contrib.auth import get_user_model
from rest_framework.reverse import reverse

from src.base.models import FlagsModel
from src.income.enums import IncomeStatus
from src.income.managers import IncomeQuerySet, ProviderQuerySet

User = get_user_model()


class Provider(FlagsModel, models.Model):
    full_name = models.CharField(
        max_length=255,
        verbose_name="Имя"
    )
    phone_number = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name="Номер телефона"
    )
    org_name = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name="Название организации"
    )
    comment = models.TextField(
        null=True,
        blank=True,
        verbose_name="Заметка"
    )
    balance = models.DecimalField(
        max_digits=19,
        decimal_places=2,
        default=0,
        verbose_name="Баланс"
    )
    created_user = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="providers",
        verbose_name="Создал"
    )

    objects = ProviderQuerySet.as_manager()

    class Meta:
        verbose_name = 'Поставщик'
        verbose_name_plural = 'Поставщики'
        ordering = ['id']

    def __str__(self):
        return f"{self.full_name} - {self.org_name}"

    def get_absolute_url(self):
        return reverse('income:provider-detail', kwargs={'pk': self.pk})


class Income(FlagsModel, models.Model):
    provider = models.ForeignKey(
        'income.Provider',
        on_delete=models.PROTECT,
        related_name="incomes",
        verbose_name="Поставщик"
    )
    total = models.DecimalField(
        max_digits=19,
        decimal_places=2,
        default=0,
        verbose_name="Сумма закупа"
    )
    total_sale_price = models.DecimalField(
        max_digits=19,
        decimal_places=2,
        default=0,
        verbose_name="Сумма цен продажи"
    )
    status = models.CharField(
        max_length=255,
        choices=IncomeStatus.choices,
        default=IncomeStatus.CREATED,
        verbose_name="Статус"
    )
    comment = models.TextField(
        null=True,
        blank=True,
        verbose_name="Заметка"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания"
    )
    created_user = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='incomes',
        verbose_name="Создал"
    )

    objects = IncomeQuerySet.as_manager()

    class Meta:
        verbose_name = 'Приход'
        verbose_name_plural = 'Приходы'
        ordering = ['-created_at']

    def __str__(self):
        return f"Приход #{self.id}"

    def get_absolute_url(self):
        return reverse('income:income-detail', kwargs={'pk': self.pk})


class IncomeItem(models.Model):
    income = models.ForeignKey(
        'income.Income',
        on_delete=models.PROTECT,
        related_name="income_item_set",
        verbose_name="Приход"
    )
    product = models.ForeignKey(
        'product.Product',
        on_delete=models.PROTECT,
        related_name='income_items',
        verbose_name="Товар"
    )
    count = models.DecimalField(
        max_digits=19,
        decimal_places=2,
        default=0,
        verbose_name="Кол-во"
    )
    price = models.DecimalField(
        max_digits=19,
        decimal_places=2,
        default=0,
        verbose_name="Цена покупки"
    )
    sale_price = models.DecimalField(
        max_digits=19,
        decimal_places=2,
        default=0,
        verbose_name="Цена продажи"
    )
    total = models.DecimalField(
        max_digits=19,
        decimal_places=2,
        default=0,
        verbose_name="Сумма"
    )
    total_sale_price = models.DecimalField(
        max_digits=19,
        decimal_places=2,
        default=0,
        verbose_name="Сумма цен продаж"
    )

    class Meta:
        verbose_name = 'Элемент прихода'
        verbose_name_plural = 'Элементы прихода'
        ordering = ['id']

    def __str__(self):
        return f"{self.income} - {self.product}"

    def get_last_price(self):
        income_item = IncomeItem.objects.filter(
            income__status=IncomeStatus.COMPLETED,
            product=self.product
        ).order_by('-income__created_at').first()
        return Decimal(income_item.price) if income_item else 0

    def get_last_sale_price(self):
        income_item = IncomeItem.objects.filter(
            income__status=IncomeStatus.COMPLETED,
            product=self.product
        ).order_by('-income__created_at').first()
        return Decimal(income_item.sale_price) if income_item else 0


class ProviderProduct(models.Model):
    product = models.ForeignKey(
        'product.Product',
        on_delete=models.CASCADE,
        related_name='providers',
        verbose_name="Товар"
    )
    provider = models.ForeignKey(
        'income.Provider',
        on_delete=models.CASCADE,
        related_name='products',
        verbose_name="Поставщик"
    )

    class Meta:
        unique_together = ['product', 'provider']
