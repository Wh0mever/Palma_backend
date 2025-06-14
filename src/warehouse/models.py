from django.db import models
from django.contrib.auth import get_user_model

from src.base.models import FlagsModel
from src.warehouse.managers import WarehouseProductQuerySet, WarehouseProductWriteOffQuerySet

User = get_user_model()


class WarehouseProduct(models.Model):
    product = models.ForeignKey(
        'product.Product',
        on_delete=models.PROTECT,
        related_name="warehouse_products",
        verbose_name="Товар"
    )
    count = models.DecimalField(
        max_digits=19,
        decimal_places=2,
        verbose_name="Кол-во"
    )
    self_price = models.DecimalField(
        max_digits=19,
        decimal_places=2,
        verbose_name="Себестоимость"
    )
    sale_price = models.DecimalField(
        max_digits=19,
        decimal_places=2,
        default=0,
        verbose_name="Цена продажи"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания"
    )
    income_item = models.ForeignKey(
        'income.IncomeItem',
        on_delete=models.CASCADE,
        related_name="warehouse_products",
        verbose_name="Элемент прихода"
    )

    objects = WarehouseProductQuerySet.as_manager()

    class Meta:
        verbose_name = 'Товар из склада'
        verbose_name_plural = 'Товары из склада'
        ordering = ['-created_at']

    def __str__(self):
        return f"Товар со склада | {self.product} | {self.created_at.strftime('%d/%m/%Y %H:%M')}"


class WarehouseProductWriteOff(FlagsModel):
    warehouse_product = models.ForeignKey(
        'warehouse.WarehouseProduct',
        on_delete=models.PROTECT,
        related_name="product_write_off_set",
        verbose_name="Товар со склада"
    )
    count = models.DecimalField(
        max_digits=19,
        decimal_places=2,
        verbose_name="Кол-во"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания"
    )
    created_user = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="user_created_write_offs",
        verbose_name="Создал"
    )
    deleted_user = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="deleted_user_write_offs",
        verbose_name="Удален"
    )
    comment = models.TextField(
        blank=True,
        null=True,
        verbose_name="Комментарий"
    )

    objects = WarehouseProductWriteOffQuerySet.as_manager()

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Списание товара"
        verbose_name_plural = "Списания товаров"

    def __str__(self):
        return f"Списание | {self.warehouse_product} | {self.created_at.strftime('%Y-%m-%d %H:%M:%S')}"
