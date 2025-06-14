from django.db import models
from django.db.models import Q
from django_filters import rest_framework as filters
from django.contrib.auth import get_user_model

from src.factory.enums import ProductFactoryStatus, ProductFactorySalesType
from src.factory.models import ProductFactory, ProductFactoryCategory
from src.order.enums import OrderStatus
from src.order.models import Client
from src.product.models import Industry
from src.user.enums import UserType

User = get_user_model()


class ProductFactoryFilter(filters.FilterSet):
    status = filters.MultipleChoiceFilter(
        field_name='status',
        null_value='',
        choices=ProductFactoryStatus.choices
    )
    sales_type = filters.MultipleChoiceFilter(
        field_name='sales_type',
        choices=ProductFactorySalesType.choices
    )
    florist = filters.ModelMultipleChoiceFilter(
        field_name='florist',
        queryset=User.objects.filter(
            type__in=(UserType.FLORIST, UserType.FLORIST_PERCENT, UserType.CRAFTER, UserType.FLORIST_ASSISTANT)
        )
    )
    industry = filters.ModelMultipleChoiceFilter(
        field_name='category__industry',
        queryset=Industry.objects.all()
    )
    category = filters.ModelMultipleChoiceFilter(
        field_name='category',
        queryset=ProductFactoryCategory.objects.all()
    )
    client = filters.ModelMultipleChoiceFilter(
        queryset=Client.objects.get_available(),
        method='by_clients'
    )

    class Meta:
        model = ProductFactory
        fields = (
            'status',
            'sales_type',
            'industry',
            'florist',
            'category',
        )

    def by_clients(self, queryset, name, value):
        if value:
            queryset = queryset.filter(
                ~Q(order_item_set__order__status=OrderStatus.CANCELLED)
                & Q(order_item_set__is_returned=False)
                & Q(order_item_set__order__client__in=value)
            ).distinct()
        return queryset
