from django.contrib.auth import get_user_model
from django.db import models
from django_resized import ResizedImageField

from src.base.models import FlagsModel
from src.factory.enums import ProductFactoryStatus, ProductFactorySalesType, FactoryTakeApartRequestType
from src.factory.managers import ProductFactoryQuerySet, ProductFactoryCategoryQuerySet, ProductFactoryItemQuerySet

User = get_user_model()


class ProductFactoryCategory(FlagsModel):
    name = models.CharField(
        max_length=255,
        verbose_name="Название"
    )
    industry = models.ForeignKey(
        'product.Industry',
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        verbose_name="Отрасль"
    )
    charge_percent = models.DecimalField(
        max_digits=19,
        decimal_places=2,
        default=0,
        verbose_name="Процент наценки"
    )

    objects = ProductFactoryCategoryQuerySet.as_manager()

    class Meta:
        verbose_name = "Категория произведенных товаров"
        verbose_name_plural = "Категории произведенных товаров"

    def __str__(self):
        return f"Категория букетов | {self.name}"


class ProductFactory(FlagsModel):
    name = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name="Название"
    )
    product_code = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        unique=True,
        verbose_name="Код"
    )
    self_price = models.DecimalField(
        max_digits=19,
        decimal_places=2,
        default=0,
        verbose_name="Себестоимость"
    )
    price = models.DecimalField(
        max_digits=19,
        decimal_places=2,
        default=0,
        verbose_name="Цена продажи"
    )
    category = models.ForeignKey(
        "factory.ProductFactoryCategory",
        on_delete=models.PROTECT,
        related_name="product_factory_set",
        verbose_name="Категория"
    )
    sales_type = models.CharField(
        max_length=255,
        choices=ProductFactorySalesType.choices,
        verbose_name="Тип продажи товара"
    )
    image = ResizedImageField(
        upload_to="images/products/%Y/%m/%d",
        size=[512, 512],
        crop=['middle', 'center'],
        quality=60,
        blank=True,
        null=True,
        verbose_name='Фото'
    )
    status = models.CharField(
        max_length=255,
        choices=ProductFactoryStatus.choices,
        default=ProductFactoryStatus.CREATED,
        verbose_name="Статус"
    )
    florist = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="owner_product_factory_set",
        verbose_name="Флорист"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания"
    )
    created_user = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="created_user_product_factory_set",
        verbose_name="Создал"
    )
    finished_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Дата окончания"
    )
    finished_user = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="finished_user_product_factory_set",
        verbose_name="Закончил"
    )
    written_off_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Дата списания"
    )
    deleted_user = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="deleted_user_product_factory_set",
        verbose_name="Удалил"
    )

    objects = ProductFactoryQuerySet.as_manager()

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Производство товара'
        verbose_name_plural = 'Производство товаров'

    def __str__(self):
        return f"{self.name}"

    def save(self, *args, **kwargs):
        if self.id:
            old_instance: ProductFactory = ProductFactory.objects.get(pk=self.id)
            if self.image and self.image != old_instance.image:
                old_instance.image.delete()
        super().save(*args, **kwargs)

    def get_items_total_sum(self):
        items = self.product_factory_item_set.all()
        return sum([item.total_price for item in items])


class ProductFactoryItem(models.Model):
    factory = models.ForeignKey(
        "factory.ProductFactory",
        on_delete=models.CASCADE,
        related_name="product_factory_item_set",
        verbose_name="Производство"
    )
    warehouse_product = models.ForeignKey(
        "warehouse.WarehouseProduct",
        on_delete=models.PROTECT,

        related_name="product_factory_item_set",
        verbose_name="Товар со склада"
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
        verbose_name="Цена"
    )
    total_self_price = models.DecimalField(
        max_digits=19,
        decimal_places=2,
        default=0,
        verbose_name="Сумма себестоимости"
    )
    total_price = models.DecimalField(
        max_digits=19,
        decimal_places=2,
        default=0,
        verbose_name="Сумма"
    )

    objects = ProductFactoryItemQuerySet.as_manager()

    class Meta:
        ordering = ['-id']
        verbose_name = "Элемент производства"
        verbose_name_plural = "Элементы производства"

    def __str__(self):
        return f"{self.factory} - {self.warehouse_product.product}"


class ProductFactoryItemReturn(FlagsModel):
    factory_item = models.ForeignKey(
        'factory.ProductFactoryItem',
        on_delete=models.PROTECT,
        related_name="product_returns",
        verbose_name="Элемент производства"
    )
    count = models.DecimalField(
        max_digits=19,
        decimal_places=2,
        default=0,
        verbose_name="Кол-во"
    )
    total_self_price = models.DecimalField(
        max_digits=19,
        decimal_places=2,
        default=0,
        verbose_name="Сумма себестоимости"
    )
    total_price = models.DecimalField(
        max_digits=19,
        decimal_places=2,
        default=0,
        verbose_name="Сумма"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Создан"
    )
    created_user = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="product_factory_returns_created_users",
        verbose_name="Создал"
    )
    deleted_user = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="product_factory_returns_deleted_users",
        verbose_name="Удалил"
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Возвращенный элемент производства"
        verbose_name_plural = "Возвращенные элемент производства"

    def __str__(self):
        return f"Возврат на склад | {self.factory_item}"


class FactoryTakeApartRequest(models.Model):
    request_type = models.CharField(
        max_length=50,
        choices=FactoryTakeApartRequestType.choices,
        verbose_name="Тип запроса"
    )
    product_factory = models.ForeignKey(
        'factory.ProductFactory',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="factory_take_apart_requests",
        verbose_name="Букет"
    )
    initial_status = models.CharField(
        max_length=50,
        choices=ProductFactoryStatus.choices,
        verbose_name="Статус при запросе"
    )
    is_sent = models.BooleanField(
        default=False,
        verbose_name="Доставлен"
    )
    is_answered = models.BooleanField(
        default=False,
        verbose_name="Отвечен"
    )
    is_accepted = models.BooleanField(
        default=False,
        verbose_name="Разрешение дано"
    )
    created_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="factory_take_apart_requests",
        verbose_name="Пользователь"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания"
    )
