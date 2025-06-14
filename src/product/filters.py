from django_filters import rest_framework as filters

from src.income.models import Provider
from src.product.models import Product, Industry


class ProductFilter(filters.FilterSet):
    industry = filters.ModelMultipleChoiceFilter(
        field_name='category__industry',
        queryset=Industry.objects.all()
    )
    providers = filters.ModelMultipleChoiceFilter(
        queryset=Provider.objects.all(),
        label='Поставщик',
        method='by_provider'
    )

    class Meta:
        model = Product
        fields = ('category', 'industry')

    def by_provider(self, queryset, name, value):
        if not value:
            return queryset
        return queryset.filter(providers__provider__in=value).distinct()