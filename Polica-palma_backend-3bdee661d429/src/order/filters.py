from django.db import models
from django_filters import rest_framework as filters
from django.contrib.auth import get_user_model

from src.order.enums import OrderStatus
from src.order.models import Order, Client
from src.product.models import Industry

User = get_user_model()


class OrderFilter(filters.FilterSet):
    industry = filters.ModelMultipleChoiceFilter(
        # field_name='created_user__industry',
        queryset=Industry.objects.all(),
        method="filter_by_industry"
    )
    status = filters.MultipleChoiceFilter(
        field_name='status',
        choices=OrderStatus.choices,
    )
    client = filters.ModelMultipleChoiceFilter(
        field_name='client',
        queryset=Client.objects.all()
    )
    created_user = filters.ModelMultipleChoiceFilter(
        field_name='created_user',
        queryset=User.objects.all()
    )
    salesman = filters.ModelMultipleChoiceFilter(
        field_name='salesman',
        queryset=User.objects.all()
    )
    has_debt = filters.BooleanFilter(label="Есть долг", method="by_has_debt")

    def by_has_debt(self, queryset, name, value):
        if value:
            return queryset.filter(
                ~models.Q(debt=0)
            )
        return queryset.filter(debt=0)

    class Meta:
        model = Order
        fields = (
            'client',
            'industry',
            'status',
            'created_user',
            'salesman',
        )

    def filter_by_industry(self, queryset, name, value):
        if not value:
            return queryset
        return queryset.by_industries(value)
