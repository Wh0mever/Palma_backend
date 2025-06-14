from django.core.validators import MaxValueValidator
from django.db import models

from src.base.models import FlagsModel
from src.product.enums import ProductUnitType
from src.product.managers import ProductQuerySet, CategoryQuerySet, IndustryQuerySet

from django_resized import ResizedImageField


class Industry(FlagsModel):
    name = models.CharField(
        max_length=255,
        verbose_name="Название"
    )
    has_sale_compensation = models.BooleanField(
        default=True,
        verbose_name="Есть доля с продаж?"
    )
    sale_compensation_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        validators=[MaxValueValidator(100)],
        verbose_name="Процент с продажи продавцу"
    )

    objects = IndustryQuerySet.as_manager()

    class Meta:
        verbose_name = 'Отрасль'
        verbose_name_plural = 'Отрасли'
        ordering = ['id']

    def __str__(self):
        return self.name


class Category(FlagsModel):
    name = models.CharField(
        max_length=255,
        verbose_name="Название"
    )
    industry = models.ForeignKey(
        'product.Industry',
        on_delete=models.PROTECT,
        verbose_name="Отрасль"
    )
    is_composite = models.BooleanField(
        default=False,
        verbose_name="Составной"
    )
    is_for_sale = models.BooleanField(
        default=True,
        verbose_name="На продажу"
    )

    objects = CategoryQuerySet.as_manager()

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ['id']

    def __str__(self):
        return self.name


class Product(FlagsModel):
    name = models.CharField(
        max_length=255,
        verbose_name="Название"
    )
    unit_type = models.CharField(
        max_length=50,
        choices=ProductUnitType.choices,
        default=ProductUnitType.PIECE,
        verbose_name="Ед. измерения"
    )
    price = models.DecimalField(
        max_digits=19,
        decimal_places=2,
        verbose_name="Цена продажи"
    )
    code = models.CharField(
        max_length=100,
        unique=True,
        null=True,
        blank=True,
        verbose_name="Код"
    )
    category = models.ForeignKey(
        'product.Category',
        on_delete=models.PROTECT,
        verbose_name='Категория'
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

    objects = ProductQuerySet.as_manager()

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'
        ordering = ['id']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.id:
            old_instance: Product = Product.objects.get(pk=self.id)
            if self.image and self.image != old_instance.image:
                old_instance.image.delete()
        super().save(*args, **kwargs)

    def is_barcode_printable(self):
        if self.code:
            if len(self.code) == 13 and self.code.startswith('1'):
                return True
        return False
