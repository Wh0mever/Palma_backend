from django_filters import rest_framework as filters
from django.contrib.auth import get_user_model
from django.utils import timezone

from src.factory.enums import ProductFactoryStatus, ProductFactorySalesType
from src.factory.models import ProductFactory, ProductFactoryCategory
from src.order.enums import OrderStatus
from src.order.models import Order, OrderItemProductReturn, OrderItemProductFactory, OrderItem, Client
from src.product.models import Industry, Category, Product
from src.user.enums import WorkerIncomeType, WorkerIncomeReason, UserType
from src.user.models import WorkerIncomes

User = get_user_model()


class OrderFilter(filters.FilterSet):
    industry = filters.ModelMultipleChoiceFilter(
        queryset=Industry.objects.all(),
        method="filter_by_industry"
    )
    status = filters.MultipleChoiceFilter(
        field_name='status',
        choices=OrderStatus.choices
    )
    client = filters.ModelMultipleChoiceFilter(
        field_name='client',
        queryset=Client.objects.all()
    )
    salesman = filters.ModelMultipleChoiceFilter(
        field_name='salesman',
        queryset=User.objects.all()
    )
    created_user = filters.ModelMultipleChoiceFilter(
        field_name='created_user',
        queryset=User.objects.all()
    )

    class Meta:
        model = Order
        fields = (
            # 'industry',
            'status',
            'client',
            'salesman',
            'created_user',
        )

    def filter_by_industry(self, queryset, name, value):
        if not value:
            return queryset
        return queryset.by_industries(value)


class OrderItemFilter(filters.FilterSet):
    client = filters.ModelMultipleChoiceFilter(
        field_name='order__client',
        queryset=Client.objects.all()
    )
    category = filters.ModelMultipleChoiceFilter(
        field_name='product__category',
        queryset=Category.objects.all()
    )
    industry = filters.ModelMultipleChoiceFilter(
        field_name='product__category__industry',
        queryset=Industry.objects.all()
    )
    created_user = filters.ModelMultipleChoiceFilter(
        field_name='order__created_user',
        queryset=User.objects.all()
    )
    salesman = filters.ModelMultipleChoiceFilter(
        field_name='order__salesman',
        queryset=User.objects.all()
    )
    product = filters.ModelMultipleChoiceFilter(
        field_name='product',
        queryset=Product.objects.all()
    )

    class Meta:
        model = OrderItem
        fields = (
            'product',
            'client',
            'category',
            'industry',
            'created_user',
            'salesman',
        )


class OrderItemProductFactoryFilter(filters.FilterSet):
    client = filters.ModelMultipleChoiceFilter(
        field_name='order__client',
        queryset=Client.objects.all()
    )
    factory_category = filters.ModelMultipleChoiceFilter(
        field_name='product_factory__category',
        queryset=Category.objects.all()
    )
    industry = filters.ModelMultipleChoiceFilter(
        field_name='product_factory__category__industry',
        queryset=Industry.objects.all()
    )
    created_user = filters.ModelMultipleChoiceFilter(
        field_name='order__created_user',
        queryset=User.objects.all()
    )
    salesman = filters.ModelMultipleChoiceFilter(
        field_name='order__salesman',
        queryset=User.objects.all()
    )

    class Meta:
        model = OrderItemProductFactory
        fields = (
            'product_factory',
            'factory_category',
            'client',
            'industry',
            'created_user',
            'salesman',
        )


class ProductFilter(filters.FilterSet):
    category = filters.ModelMultipleChoiceFilter(
        field_name='category',
        queryset=Category.objects.all()
    )
    industry = filters.ModelMultipleChoiceFilter(
        field_name='category__industry',
        queryset=Industry.objects.all()
    )

    class Meta:
        model = Product
        fields = (
            'category',
            'industry',
        )


class OrderItemReturnFilter(filters.FilterSet):
    industry = filters.ModelMultipleChoiceFilter(
        field_name='order_item__product__category__industry',
        queryset=Industry.objects.all()
    )
    category = filters.ModelMultipleChoiceFilter(
        field_name='order_item__product__category',
        queryset=Category.objects.all()
    )

    class Meta:
        model = OrderItemProductReturn
        fields = (
            'industry',
            'category'
        )


class OrderItemProductFactoryReturnFilter(filters.FilterSet):
    industry = filters.ModelMultipleChoiceFilter(
        field_name='product_factory__category__industry',
        queryset=Industry.objects.all()
    )
    factory_category = filters.ModelMultipleChoiceFilter(
        field_name='product_factory__category',
        queryset=ProductFactoryCategory.objects.all()
    )

    class Meta:
        model = OrderItemProductFactory
        fields = (
            'industry',
            'factory_category'
        )


class WriteOffReportProductFilter(filters.FilterSet):
    industry = filters.ModelMultipleChoiceFilter(
        field_name='category__industry',
        queryset=Industry.objects.all()
    )
    category = filters.ModelMultipleChoiceFilter(
        field_name='category',
        queryset=Category.objects.all()
    )

    class Meta:
        model = Product
        fields = (
            'industry',
            'category'
        )


class WriteOffReportProductFactoryFilter(filters.FilterSet):
    factory_category = filters.ModelMultipleChoiceFilter(
        field_name='category',
        queryset=ProductFactoryCategory.objects.all()
    )

    class Meta:
        model = ProductFactory
        fields = (
            'factory_category',
        )


class ProductFactoriesReportProductFactoryFilter(filters.FilterSet):
    category = filters.ModelMultipleChoiceFilter(
        field_name='category',
        queryset=ProductFactoryCategory.objects.all()
    )
    florist = filters.ModelMultipleChoiceFilter(
        field_name='florist',
        queryset=User.objects.all()
    )
    status = filters.MultipleChoiceFilter(
        field_name='status',
        choices=ProductFactoryStatus.choices
    )
    sales_type = filters.MultipleChoiceFilter(
        field_name='sales_type',
        choices=ProductFactorySalesType.choices
    )

    class Meta:
        model = ProductFactory
        fields = (
            'category',
            'florist',
            'status',
            'sales_type'
        )


class WorkerIncomeFilter(filters.FilterSet):
    income_type = filters.MultipleChoiceFilter(
        field_name='income_type',
        choices=WorkerIncomeType.choices
    )
    income_reason = filters.MultipleChoiceFilter(
        field_name='reason',
        choices=WorkerIncomeReason.choices
    )

    class Meta:
        model = WorkerIncomes
        fields = ('income_type', 'income_reason')


class WorkersFilter(filters.FilterSet):
    worker_type = filters.MultipleChoiceFilter(
        field_name='type',
        choices=UserType.choices
    )

    class Meta:
        model = User
        fields = ('worker_type',)