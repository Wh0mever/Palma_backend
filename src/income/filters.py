from django_filters import rest_framework as filters

from src.income.enums import IncomeStatus
from src.income.models import Income, Provider
from src.product.models import Industry


class IncomeFilterSet(filters.FilterSet):
    industry = filters.ModelMultipleChoiceFilter(
        field_name='provider__created_user__industry',
        queryset=Industry.objects.all()
    )
    provider = filters.ModelMultipleChoiceFilter(
        field_name='provider',
        queryset=Provider.objects.all()
    )
    status = filters.MultipleChoiceFilter(
        field_name='status',
        choices=IncomeStatus.choices
    )


    class Meta:
        model = Income
        fields = 'status', 'industry', 'provider'
