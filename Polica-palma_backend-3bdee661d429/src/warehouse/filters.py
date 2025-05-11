from django_filters import rest_framework as filters

from src.product.models import Industry, Category
from src.warehouse.models import WarehouseProduct, WarehouseProductWriteOff


class WarehouseProductFilter(filters.FilterSet):
    industry = filters.ModelMultipleChoiceFilter(
        field_name='product__category__industry',
        queryset=Industry.objects.all()
    )
    category = filters.ModelMultipleChoiceFilter(
        field_name='product__category',
        queryset=Category.objects.all()
    )

    class Meta:
        model = WarehouseProduct
        fields = (
            'category',
            'industry'
        )


class WarehouseProductWriteOffFilter(filters.FilterSet):
    industry = filters.ModelMultipleChoiceFilter(
        field_name='warehouse_product__product__category__industry',
        queryset=Industry.objects.all()
    )
    category = filters.ModelMultipleChoiceFilter(
        field_name='warehouse_product__product__category',
        queryset=Category.objects.all()
    )

    class Meta:
        model = WarehouseProductWriteOff
        fields = (
            'category',
            'industry'
        )