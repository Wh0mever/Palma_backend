from django_filters import rest_framework as filters
from django.contrib.auth import get_user_model

from src.payment.enums import PaymentModelType, OutlayType
from src.payment.models import Payment, PaymentMethod, Outlay
from src.order.models import Client

User = get_user_model()

PAYMENT_MODEL_TYPES = [
    ("OUTLAY", "Расходы"),
    ("ORDER", "Заказ"),
    ("INCOME", "Расход поставщикам"),
]

class PaymentFilter(filters.FilterSet):
    payment_method = filters.ModelMultipleChoiceFilter(
        field_name='payment_method',
        queryset=PaymentMethod.objects.all()
    )
    payment_model_type = filters.MultipleChoiceFilter(
        method='by_model_type',
        field_name='payment_model_type',
        choices=PAYMENT_MODEL_TYPES
    )
    outlay = filters.ModelMultipleChoiceFilter(
        field_name="outlay",
        queryset=Outlay.objects.get_available()
    )
    created_user = filters.ModelMultipleChoiceFilter(
        field_name='created_user',
        queryset=User.objects.all()
    )
    worker = filters.ModelMultipleChoiceFilter(
        field_name="worker",
        queryset=User.objects.all()
    )
    client = filters.ModelMultipleChoiceFilter(
        field_name="client",
        queryset=Client.objects.all()
    )
    is_debt = filters.BooleanFilter(
        field_name="is_debt"
    )

    def by_model_type(self,  queryset, name, value: list):
        if 'INCOME' in value:
            value.append('PROVIDER')
        lookup = '__'.join([name, 'in'])
        queryset = queryset.filter(**{lookup: value})
        return queryset

    class Meta:
        model = Payment
        fields = ['payment_method', 'payment_type', 'payment_model_type', 'outlay',
                  'client', 'created_user', 'worker', 'is_debt']


class OutlayFilter(filters.FilterSet):
    outlay_type = filters.MultipleChoiceFilter(
        field_name='outlay_type',
        choices=OutlayType.choices
    )

    class Meta:
        model = Outlay
        fields = ['outlay_type']
