from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models
from django.contrib.auth import get_user_model
from rest_framework.reverse import reverse

from src.base.models import FlagsModel
from src.order.enums import OrderStatus
from src.order.managers import OrderItemQuerySet, OrderQuerySet, ClientQuerySet, OrderItemProductFactoryQuerySet
from src.payment.enums import PaymentType
from src.payment.models import Payment

User = get_user_model()


class Client(FlagsModel, models.Model):
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
    comment = models.TextField(
        null=True,
        blank=True,
        verbose_name="Заметка"
    )
    discount_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        verbose_name="Процент скидки"
    )

    objects = ClientQuerySet.as_manager()

    class Meta:
        verbose_name = 'Клиент'
        verbose_name_plural = 'Клиенты'
        ordering = ['-id']

    def __str__(self):
        return f"{self.full_name}"

    def get_absolute_url(self):
        return reverse('order:client-detail', kwargs={'pk': self.pk})

    def get_debt(self):
        # TODO: Should filter orders by status
        orders = Order.objects.get_available().filter(models.Q(client=self) & ~models.Q(status=OrderStatus.CANCELLED))
        total_debt = orders.aggregate(total_debt=models.Sum('debt', default=0)).get('total_debt')
        return total_debt


class Order(FlagsModel, models.Model):
    client = models.ForeignKey(
        'order.Client',
        on_delete=models.PROTECT,
        related_name="orders",
        verbose_name="Клиент"
    )
    department = models.ForeignKey(
        'order.Department',
        on_delete=models.PROTECT,
        null=True,
        related_name="orders",
        verbose_name="Отдел"

    )
    status = models.CharField(
        max_length=100,
        choices=OrderStatus.choices,
        default=OrderStatus.CREATED,
        verbose_name="Статус"
    )
    discount = models.DecimalField(
        max_digits=19,
        decimal_places=2,
        default=0,
        verbose_name="Скидка"
    )
    total = models.DecimalField(
        max_digits=19,
        decimal_places=2,
        default=0,
        verbose_name="Сумма"
    )
    debt = models.DecimalField(
        max_digits=19,
        default=0,
        decimal_places=2,
        verbose_name="Долг"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания"
    )
    salesman = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="attached_orders",
        null=True,
        blank=True,
        verbose_name="Продавец"
    )
    created_user = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="orders",
        verbose_name="Создал"
    )
    completed_user = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="completed_orders",
        blank=True,
        null=True,
        verbose_name="Завершил"
    )
    comment = models.TextField(
        blank=True,
        null=True,
        verbose_name="Комментарий"
    )

    objects = OrderQuerySet.as_manager()

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
        ordering = ['-created_at']

    def __str__(self):
        return f"Заказ #{self.id}"

    def get_absolute_url(self):
        return reverse('order:order-detail', kwargs={'pk': self.pk})

    def get_total_with_discount(self):
        return self.total - self.discount

    def get_amount_paid(self):
        amount_paid = Payment.objects.filter(
            order=self,
            is_deleted=False,
            payment_type=PaymentType.INCOME
        ).aggregate(amount_sum=models.Sum('amount', default=0)).get('amount_sum')

        return amount_paid

    def get_amount_money_returned(self):
        amount_returned = Payment.objects.filter(
            order=self,
            is_deleted=False,
            payment_type=PaymentType.OUTCOME
        ).aggregate(amount_sum=models.Sum('amount', default=0)).get('amount_sum')

        return amount_returned


class OrderItem(models.Model):
    order = models.ForeignKey(
        'order.Order',
        on_delete=models.PROTECT,
        related_name="order_items",
        verbose_name="Заказ"
    )
    product = models.ForeignKey(
        'product.Product',
        on_delete=models.PROTECT,
        related_name='order_items',
        verbose_name="Товар со склада"
    )
    price = models.DecimalField(
        max_digits=19,
        decimal_places=2,
        default=0,
        verbose_name="Цена"
    )
    discount = models.DecimalField(
        max_digits=19,
        decimal_places=2,
        default=0,
        verbose_name="Скидка"
    )
    count = models.DecimalField(
        max_digits=19,
        decimal_places=2,
        default=0,
        verbose_name="Кол-во"
    )
    total = models.DecimalField(
        max_digits=19,
        default=0,
        decimal_places=2,
        verbose_name="Сумма"
    )

    objects = OrderItemQuerySet.as_manager()

    class Meta:
        verbose_name = 'Элемент заказа'
        verbose_name_plural = 'Элементы заказа'
        ordering = ['id']

    def __str__(self):
        return f"{self.order} | {self.product}"


class Department(FlagsModel, models.Model):
    name = models.CharField(
        max_length=250,
        verbose_name="Название"
    )

    class Meta:
        verbose_name = "Отдел"
        verbose_name_plural = "Отделы"
        ordering = ['id']

    def __str__(self):
        return self.name


class OrderItemProductOutcome(models.Model):
    warehouse_product = models.ForeignKey(
        'warehouse.WarehouseProduct',
        on_delete=models.PROTECT,
        related_name="product_outcomes",
        verbose_name="Товар"
    )
    order_item = models.ForeignKey(
        'order.OrderItem',
        on_delete=models.CASCADE,
        related_name="product_outcomes",
        verbose_name="Элемент заказа"
    )
    count = models.DecimalField(
        max_digits=19,
        decimal_places=2,
        verbose_name="Количество"
    )

    def __str__(self):
        return f"{self.order_item.order} | {self.warehouse_product}"


class OrderItemProductReturn(FlagsModel):
    order = models.ForeignKey(
        'order.Order',
        on_delete=models.CASCADE,
        related_name="product_returns",
        verbose_name="Заказ"
    )
    order_item = models.ForeignKey(
        'order.OrderItem',
        on_delete=models.CASCADE,
        related_name="product_returns",
        verbose_name="Элемент заказа"
    )
    count = models.DecimalField(
        max_digits=19,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(1)],
        verbose_name="Количество"
    )
    total = models.DecimalField(
        max_digits=19,
        decimal_places=2,
        default=0,
        verbose_name="Сумма"
    )
    total_self_price = models.DecimalField(
        max_digits=19,
        decimal_places=2,
        default=0,
        verbose_name="Сумма себестоимости"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Создан"
    )
    created_user = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="product_returns_created_users",
        verbose_name="Создал"
    )
    deleted_user = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="product_returns_deleted_users",
        verbose_name="Удалил"
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Возврат товаров'
        verbose_name_plural = 'Возвраты товаров'

    def __str__(self):
        return f"Возврат - {self.order_item.order}"


class OrderItemProductFactory(models.Model):
    order = models.ForeignKey(
        "order.Order",
        on_delete=models.CASCADE,
        related_name="order_item_product_factory_set",
        verbose_name="Заказ"
    )
    product_factory = models.ForeignKey(
        "factory.ProductFactory",
        on_delete=models.PROTECT,
        related_name="order_item_set",
        verbose_name="Товар из производства"
    )
    price = models.DecimalField(
        max_digits=19,
        decimal_places=2,
        verbose_name="Цена"
    )
    is_returned = models.BooleanField(
        default=False,
        verbose_name="Возвращен"
    )
    returned_user = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="order_item_product_factory_set",
        null=True,
        blank=True,
        verbose_name="Вернул"
    )
    returned_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Дата возврата"
    )
    discount = models.DecimalField(
        max_digits=19,
        decimal_places=2,
        default=0,
        verbose_name="Скидка"
    )

    objects = OrderItemProductFactoryQuerySet.as_manager()

    class Meta:
        ordering = ['id']
        verbose_name = "Элемент заказа из произвдства"
        verbose_name_plural = "Элементы заказа из произвдства"

    def __str__(self):
        return f"{self.order} | {self.product_factory}"
