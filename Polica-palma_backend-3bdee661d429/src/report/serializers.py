import decimal

from django.db import models
from django.db.models import QuerySet
from django.contrib.auth import get_user_model
from rest_framework import serializers

from src.factory.models import ProductFactoryItemReturn, ProductFactory, ProductFactoryCategory
from src.factory.serializers import ProductFactorySerializer
from src.income.models import Income
from src.income.serializers import ProviderSerializer
from src.order.models import Order, OrderItemProductReturn, Client, OrderItemProductFactory, OrderItem
from src.order.serializers import ClientSerializer, OrderListSerializer
from src.payment.models import Payment
from src.product.models import Product
from src.product.serializers import IndustrySerializer, CategorySerializer, ProductSerializer
from src.user.models import WorkerIncomes
from src.user.serializers import UserSerializer
from src.warehouse.models import WarehouseProductWriteOff

User = get_user_model()


class OrderListReportSerializer(serializers.ModelSerializer):
    amount_paid = serializers.DecimalField(read_only=True, max_digits=19, decimal_places=2)
    industry = IndustrySerializer(read_only=True, source='salesman.industry')
    created_user = UserSerializer(read_only=True)
    completed_user = UserSerializer(read_only=True)
    salesman = UserSerializer(read_only=True)
    total = serializers.SerializerMethodField(read_only=True)
    total_with_discount = serializers.DecimalField(read_only=True, max_digits=19, decimal_places=2)
    total_discount = serializers.DecimalField(read_only=True, max_digits=19, decimal_places=2)
    total_charge = serializers.DecimalField(read_only=True, max_digits=19, decimal_places=2)
    total_self_price = serializers.DecimalField(read_only=True, max_digits=19, decimal_places=2)
    total_profit = serializers.DecimalField(read_only=True, max_digits=19, decimal_places=2)

    class Meta:
        model = Order
        fields = (
            'id',
            'total',
            'total_with_discount',
            'amount_paid',
            'total_discount',
            'total_charge',
            'total_self_price',
            'total_profit',
            'debt',
            'client',
            'salesman',
            'industry',
            'status',
            'created_user',
            'completed_user',
            'created_at'
        )

    def get_total(self, obj):
        return str(obj.total + obj.products_discount - obj.total_charge)


class OrderReportSerializer(serializers.Serializer):
    total_sale_amount = serializers.DecimalField(max_digits=19, decimal_places=2, read_only=True)
    total_sale_with_discount_amount = serializers.DecimalField(max_digits=19, decimal_places=2, read_only=True)
    total_discount_amount = serializers.DecimalField(max_digits=19, decimal_places=2, read_only=True)
    total_charge_amount = serializers.DecimalField(max_digits=19, decimal_places=2, read_only=True)
    total_self_price_amount = serializers.DecimalField(max_digits=19, decimal_places=2, read_only=True)
    total_profit_amount = serializers.DecimalField(max_digits=19, decimal_places=2, read_only=True)
    total_debt_amount = serializers.DecimalField(max_digits=19, decimal_places=2, read_only=True)
    total_paid_amount = serializers.DecimalField(max_digits=19, decimal_places=2, read_only=True)
    orders = OrderListReportSerializer(many=True)

    @classmethod
    def create_(
            cls,
            orders,
            context=None,
            **kwargs,
    ):
        if not context:
            context = {}
        serializer = cls(
            instance=dict(orders=orders, **kwargs),
            context=context
        )
        return serializer


class MaterialReportProductListSerializer(serializers.ModelSerializer):
    total_income_in_range = serializers.DecimalField(max_digits=19, decimal_places=2)
    total_outcome_in_range = serializers.DecimalField(max_digits=19, decimal_places=2)
    before_count = serializers.DecimalField(max_digits=19, decimal_places=2)
    after_count = serializers.DecimalField(max_digits=19, decimal_places=2)
    # before_count = serializers.SerializerMethodField()
    # after_count = serializers.SerializerMethodField()
    current_count = serializers.DecimalField(max_digits=19, decimal_places=2, source='in_stock')

    class Meta:
        model = Product
        fields = (
            'id',
            'name',
            'total_income_in_range',
            'total_outcome_in_range',
            'current_count',
            'before_count',
            'after_count',
        )

    # def get_before_count(self, obj):
    #     total_income = obj.total_income_in_range + obj.total_income_after_range
    #     total_outcome = obj.total_outcome_in_range + obj.total_outcome_after_range
    #     return str(obj.in_stock - total_income + total_outcome)
    #
    # def get_after_count(self, obj):
    #     return str(obj.in_stock - (obj.total_income_after_range - obj.total_outcome_after_range))


class MaterialReportSerializer(serializers.Serializer):
    products = MaterialReportProductListSerializer(many=True)

    @classmethod
    def create_(
            cls,
            products,
            context=None,
    ):
        if not context:
            context = {}
        serializer = cls(
            instance=dict(
                products=products
            ),
            context=context
        )
        return serializer


class MaterialReportOrderListSerializer(serializers.ModelSerializer):
    product_count = serializers.DecimalField(max_digits=19, decimal_places=2)
    total_product_sum = serializers.DecimalField(max_digits=19, decimal_places=2)
    total_product_discount = serializers.DecimalField(max_digits=19, decimal_places=2)
    order_name = serializers.CharField(source='__str__', read_only=True)
    created_user = UserSerializer(read_only=True)
    salesman = UserSerializer(read_only=True)
    client = ClientSerializer(read_only=True)

    class Meta:
        model = Order
        fields = ('id', 'order_name', 'product_count', 'total_product_sum', 'total_product_discount',
                  'client', 'created_user', 'created_at', 'salesman')


class MaterialReportOrderItemReturnListSerializer(serializers.ModelSerializer):
    order_name = serializers.CharField(source='order.__str__', read_only=True)
    created_user = UserSerializer(read_only=True)

    class Meta:
        model = OrderItemProductReturn
        fields = ('id', 'count', 'order_name', 'created_user', 'created_at')


class MaterialReportFactoryItemReturnListSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='factory_item.factory.name', read_only=True)
    created_user = UserSerializer(read_only=True)

    class Meta:
        model = ProductFactoryItemReturn
        fields = ('id', 'product_name', 'count', 'created_user', 'created_at')


class MaterialReportIncomeListSerializer(serializers.ModelSerializer):
    product_count = serializers.DecimalField(max_digits=19, decimal_places=2, read_only=True)
    provider = ProviderSerializer(read_only=True)

    class Meta:
        model = Income
        fields = ('id', 'product_count', 'provider', 'created_at', 'created_user')


class MaterialReportProductFactoryListSerializer(serializers.ModelSerializer):
    product_count = serializers.DecimalField(max_digits=19, decimal_places=2)
    florist = UserSerializer(read_only=True)
    created_user = UserSerializer(read_only=True)

    class Meta:
        model = ProductFactory
        fields = ('id', 'name', 'product_count', 'florist', 'created_at', 'created_user')


class MaterialReportWriteOffListSerializer(serializers.ModelSerializer):
    created_user = UserSerializer(read_only=True)

    class Meta:
        model = WarehouseProductWriteOff
        fields = ('id', 'count', 'created_at', 'created_user')


class MaterialReportDetailSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=250)
    total_income_in_range = serializers.DecimalField(max_digits=19, decimal_places=2, read_only=True)
    total_outcome_in_range = serializers.DecimalField(max_digits=19, decimal_places=2, read_only=True)
    # total_income_after_range = serializers.DecimalField(max_digits=19, decimal_places=2, read_only=True)
    # total_outcome_after_range = serializers.DecimalField(max_digits=19, decimal_places=2, read_only=True)
    # total_income_before_range = serializers.DecimalField(max_digits=19, decimal_places=2, read_only=True)
    # total_outcome_before_range = serializers.DecimalField(max_digits=19, decimal_places=2, read_only=True)
    before_count = serializers.DecimalField(max_digits=19, decimal_places=2, read_only=True)
    after_count = serializers.DecimalField(max_digits=19, decimal_places=2, read_only=True)
    current_count = serializers.DecimalField(max_digits=19, decimal_places=2)
    # product_in_orders_count = serializers.DecimalField(max_digits=19, decimal_places=2, read_only=True)
    # product_in_incomes_count = serializers.DecimalField(max_digits=19, decimal_places=2, read_only=True)
    # product_in_factories_count = serializers.DecimalField(max_digits=19, decimal_places=2, read_only=True)
    # product_write_offs_count = serializers.DecimalField(max_digits=19, decimal_places=2, read_only=True)
    # product_order_returns_count = serializers.DecimalField(max_digits=19, decimal_places=2, read_only=True)
    # product_factory_returns_count = serializers.DecimalField(max_digits=19, decimal_places=2, read_only=True)
    total_sales_in_range = serializers.DecimalField(max_digits=19, decimal_places=2, read_only=True)
    total_self_price_in_range = serializers.DecimalField(max_digits=19, decimal_places=2, read_only=True)
    total_sales_count = serializers.DecimalField(max_digits=19, decimal_places=2, read_only=True)

    @classmethod
    def create_(
            cls,
            context=None,
            **kwargs
    ):
        if not context:
            context = {}
        serializer = cls(
            instance=dict(
                **kwargs
            ),
            context=context
        )
        return serializer


class SalesmenReportWorkerListSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='get_full_name')
    industry = IndustrySerializer()
    orders_count = serializers.DecimalField(max_digits=19, decimal_places=2)
    order_total_sum = serializers.DecimalField(max_digits=19, decimal_places=2)
    # get_sold_products_sum = serializers.DecimalField(max_digits=19, decimal_places=2)
    # get_sold_product_factories_sum = serializers.DecimalField(max_digits=19, decimal_places=2)
    income_sum = serializers.DecimalField(max_digits=19, decimal_places=2)
    payment_sum = serializers.DecimalField(max_digits=19, decimal_places=2)

    class Meta:
        model = User
        fields = (
            'id',
            'name',
            'industry',
            'balance',
            'orders_count',
            'order_total_sum',
            'income_sum',
            'payment_sum',
        )


class SalesmenReportSummarySerializer(serializers.Serializer):
    total_orders_count = serializers.DecimalField(max_digits=19, decimal_places=2)
    total_orders_sum = serializers.DecimalField(max_digits=19, decimal_places=2)
    total_income_sum = serializers.DecimalField(max_digits=19, decimal_places=2)
    total_payments_sum = serializers.DecimalField(max_digits=19, decimal_places=2)


class WorkerIncomeSerializer(serializers.ModelSerializer):
    income_name = serializers.SerializerMethodField()

    class Meta:
        model = WorkerIncomes
        fields = (
            'id', 'income_name', 'order', 'product_factory', 'total', 'income_type', 'reason', 'created_at', 'comment'
        )

    def get_income_name(self, obj):
        return f"Начисление #{obj.id}"


class WorkerPaymentSerializer(serializers.ModelSerializer):
    payment_name = serializers.SerializerMethodField()

    class Meta:
        model = Payment
        fields = ('id', 'payment_name', 'amount', 'payment_type', 'payment_model_type', 'created_at', 'comment')

    def get_payment_name(self, obj):
        return f"Платеж #{obj.id}"


class SalesmenReportOrderSerializer(serializers.ModelSerializer):
    order_name = serializers.CharField(source="__str__")
    total_with_discount = serializers.DecimalField(max_digits=19, decimal_places=2)

    class Meta:
        model = Order
        fields = ('id', 'order_name', 'total_with_discount', 'created_at')


class SalesmenReportDetailSerializer(SalesmenReportWorkerListSerializer):
    income_for_orders_sum = serializers.DecimalField(max_digits=19, decimal_places=2)
    income_for_factories_sum = serializers.DecimalField(max_digits=19, decimal_places=2)

    class Meta(SalesmenReportWorkerListSerializer.Meta):
        model = User
        fields = SalesmenReportWorkerListSerializer.Meta.fields + ('income_for_orders_sum', 'income_for_factories_sum')


class OtherWorkersReportListSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='get_full_name')
    # income_sum = serializers.DecimalField(max_digits=19, decimal_places=2)
    payment_sum = serializers.DecimalField(max_digits=19, decimal_places=2)

    class Meta:
        model = User
        fields = (
            'id',
            'name',
            'balance',
            # 'income_sum',
            'payment_sum',
        )


class OtherWorkersReportSummarySerializer(serializers.Serializer):
    # total_income_sum = serializers.DecimalField(max_digits=19, decimal_places=2)
    total_payments_sum = serializers.DecimalField(max_digits=19, decimal_places=2)


class FloristsReportFloristListSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='get_full_name')
    sold_product_count = serializers.DecimalField(max_digits=19, decimal_places=2)
    finished_product_count = serializers.DecimalField(max_digits=19, decimal_places=2)
    written_off_product_count = serializers.DecimalField(max_digits=19, decimal_places=2)
    total_product_count = serializers.SerializerMethodField()
    income_sum = serializers.DecimalField(max_digits=19, decimal_places=2)
    payment_sum = serializers.DecimalField(max_digits=19, decimal_places=2)

    class Meta:
        model = User
        fields = (
            'id',
            'name',
            'type',
            'finished_product_count',
            'sold_product_count',
            'written_off_product_count',
            'total_product_count',
            'income_sum',
            'payment_sum',
            'balance'
        )

    def get_total_product_count(self, obj):
        return str(obj.sold_product_count + obj.finished_product_count + obj.written_off_product_count)


class FloristReportSummarySerializer(serializers.Serializer):
    total_sold_product_count = serializers.DecimalField(max_digits=19, decimal_places=2)
    total_finished_product_count = serializers.DecimalField(max_digits=19, decimal_places=2)
    total_written_off_product_count = serializers.DecimalField(max_digits=19, decimal_places=2)
    total_product_count = serializers.DecimalField(max_digits=19, decimal_places=2)
    total_income_sum = serializers.DecimalField(max_digits=19, decimal_places=2)
    total_payment_sum = serializers.DecimalField(max_digits=19, decimal_places=2)


class FloristReportProductFactoryCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductFactoryCategory
        fields = ('id', 'name')


class FloristReportProductFactorySerializer(serializers.ModelSerializer):
    category = FloristReportProductFactoryCategorySerializer()

    class Meta:
        model = ProductFactory
        fields = ('id', 'name', 'product_code', 'category', 'sales_type', 'price', 'self_price')


class FloristReportDetailSerializer(FloristsReportFloristListSerializer):
    income_for_orders_sum = serializers.DecimalField(max_digits=19, decimal_places=2)
    income_for_factories_sum = serializers.DecimalField(max_digits=19, decimal_places=2)

    class Meta(FloristsReportFloristListSerializer.Meta):
        model = User
        fields = FloristsReportFloristListSerializer.Meta.fields + ('income_for_orders_sum', 'income_for_factories_sum')


# ======================= WorkersReport ====================== #

class WorkersReportWorkerListSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='get_full_name')
    industry = IndustrySerializer()
    orders_count = serializers.DecimalField(max_digits=19, decimal_places=2)
    order_total_sum = serializers.DecimalField(max_digits=19, decimal_places=2)
    sold_product_count = serializers.DecimalField(max_digits=19, decimal_places=2, default=0)
    finished_product_count = serializers.DecimalField(max_digits=19, decimal_places=2, default=0)
    written_off_product_count = serializers.DecimalField(max_digits=19, decimal_places=2, default=0)
    # total_product_count = serializers.DecimalField(max_digits=19, decimal_places=2)
    total_product_count = serializers.SerializerMethodField()
    income_sum = serializers.DecimalField(max_digits=19, decimal_places=2)
    payment_sum = serializers.DecimalField(max_digits=19, decimal_places=2)

    class Meta:
        model = User
        fields = (
            'id',
            'industry',
            'name',
            'type',
            'orders_count',
            'order_total_sum',
            'finished_product_count',
            'sold_product_count',
            'written_off_product_count',
            'total_product_count',
            'income_sum',
            'payment_sum',
            'balance'
        )

    def get_total_product_count(self, obj):
        return str(obj.sold_product_count + obj.finished_product_count + obj.written_off_product_count)


class WorkersReportSummarySerializer(serializers.Serializer):
    total_orders_count = serializers.DecimalField(max_digits=19, decimal_places=2)
    total_orders_sum = serializers.DecimalField(max_digits=19, decimal_places=2)
    total_sold_product_count = serializers.DecimalField(max_digits=19, decimal_places=2)
    total_finished_product_count = serializers.DecimalField(max_digits=19, decimal_places=2)
    total_written_off_product_count = serializers.DecimalField(max_digits=19, decimal_places=2)
    total_product_count = serializers.DecimalField(max_digits=19, decimal_places=2)
    total_income_sum = serializers.DecimalField(max_digits=19, decimal_places=2)
    total_payments_sum = serializers.DecimalField(max_digits=19, decimal_places=2)


class WorkersReportDetailSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='get_full_name')
    orders_count = serializers.DecimalField(max_digits=19, decimal_places=2)
    order_total_sum = serializers.DecimalField(max_digits=19, decimal_places=2)
    sold_product_count = serializers.DecimalField(max_digits=19, decimal_places=2)
    finished_product_count = serializers.DecimalField(max_digits=19, decimal_places=2)
    written_off_product_count = serializers.DecimalField(max_digits=19, decimal_places=2)
    total_product_count = serializers.DecimalField(max_digits=19, decimal_places=2)
    income_sum = serializers.DecimalField(max_digits=19, decimal_places=2)
    payment_sum = serializers.DecimalField(max_digits=19, decimal_places=2)
    income_for_orders_sum = serializers.DecimalField(max_digits=19, decimal_places=2)
    income_for_factories_sum = serializers.DecimalField(max_digits=19, decimal_places=2)

    class Meta(FloristsReportFloristListSerializer.Meta):
        model = User
        fields = (
            'id',
            'name',
            'orders_count',
            'order_total_sum',
            'sold_product_count',
            'finished_product_count',
            'written_off_product_count',
            'total_product_count',
            'income_sum',
            'payment_sum',
            'income_for_orders_sum',
            'income_for_factories_sum'
        )


class WriteOffsReportProductListSerializer(serializers.ModelSerializer):
    product_count = serializers.DecimalField(max_digits=19, decimal_places=2)
    self_price_sum = serializers.DecimalField(max_digits=19, decimal_places=2)
    category = CategorySerializer()

    class Meta:
        model = Product
        fields = (
            'id',
            'name',
            'code',
            'category',
            'product_count',
            'self_price_sum'
        )


class WriteOffsReportProductFactoryListSerializer(serializers.ModelSerializer):
    code = serializers.CharField(source='product_code')
    product_count = serializers.DecimalField(max_digits=19, decimal_places=2, default=1)
    self_price_sum = serializers.DecimalField(source='self_price', max_digits=19, decimal_places=2)
    category = FloristReportProductFactoryCategorySerializer()

    class Meta:
        model = ProductFactory
        fields = (
            'id',
            'name',
            'code',
            'category',
            'product_count',
            'self_price_sum',
            'written_off_at',
        )


class WriteOffsReportSummarySerializer(serializers.Serializer):
    total_product_count = serializers.DecimalField(max_digits=19, decimal_places=2, default=0)
    total_self_price_sum = serializers.DecimalField(max_digits=19, decimal_places=2, default=0)
    total_product_factory_count = serializers.DecimalField(max_digits=19, decimal_places=2, default=0)
    total_product_factory_self_price_sum = serializers.DecimalField(max_digits=19, decimal_places=2, default=0)
    total_count = serializers.DecimalField(max_digits=19, decimal_places=2, default=0)
    total_self_price = serializers.DecimalField(max_digits=19, decimal_places=2, default=0)


class WriteOffsReportProductWriteOffSerializer(serializers.ModelSerializer):
    created_user = UserSerializer()
    self_price = serializers.DecimalField(source='warehouse_product.self_price', max_digits=19, decimal_places=2)

    class Meta:
        model = WarehouseProductWriteOff
        fields = (
            'id',
            'count',
            'self_price',
            'created_at',
            'created_user',
            'comment'
        )


class WriteOffsReportsDetailSerializer(serializers.Serializer):
    product = WriteOffsReportProductListSerializer()
    product_write_offs = WriteOffsReportProductWriteOffSerializer(many=True)

    @classmethod
    def create_(
            cls,
            product,
            product_write_offs,
            context=None,
    ):
        if not context:
            context = {}
        serializer = cls(
            instance=dict(
                product=product,
                product_write_offs=product_write_offs,
            ),
            context=context
        )
        return serializer


class ClientsReportClientListSerializer(serializers.ModelSerializer):
    debt = serializers.DecimalField(max_digits=19, decimal_places=2)
    orders_count = serializers.DecimalField(max_digits=19, decimal_places=2)
    orders_sum = serializers.DecimalField(max_digits=19, decimal_places=2)
    total_discount_sum = serializers.DecimalField(max_digits=19, decimal_places=2)

    class Meta:
        model = Client
        fields = (
            'id',
            'full_name',
            'phone_number',
            'debt',
            'orders_count',
            'orders_sum',
            'total_discount_sum',
        )


class ClientsReportSerializer(serializers.Serializer):
    total_debt = serializers.DecimalField(max_digits=19, decimal_places=2)
    total_orders_count = serializers.DecimalField(max_digits=19, decimal_places=2)
    total_orders_sum = serializers.DecimalField(max_digits=19, decimal_places=2)
    clients = ClientsReportClientListSerializer(many=True)


class ClientsReportOrderSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='__str__')
    total_with_discount = serializers.DecimalField(max_digits=19, decimal_places=2)
    total_discount = serializers.DecimalField(max_digits=19, decimal_places=2)
    created_user = UserSerializer()
    completed_user = UserSerializer()
    salesman = UserSerializer()

    class Meta:
        model = Order
        fields = (
            'id',
            'name',
            'debt',
            'total_with_discount',
            'total_discount',
            'created_at',
            'created_user',
            'completed_user',
            'salesman',
        )


class ClientsReportDetailSerializer(serializers.Serializer):
    client = ClientsReportClientListSerializer()
    orders = ClientsReportOrderSerializer(many=True)

    @classmethod
    def create_(
            cls,
            client,
            orders,
            context=None,
    ):
        if not context:
            context = {}
        serializer = cls(
            instance=dict(
                client=client,
                orders=orders,
            ),
            context=context
        )
        return serializer


class ProductFactoriesReportProductListSerializer(serializers.ModelSerializer):
    florist = UserSerializer()
    category = FloristReportProductFactoryCategorySerializer()
    sold_price = serializers.DecimalField(max_digits=19, decimal_places=2)

    class Meta:
        model = ProductFactory
        fields = (
            'id',
            'name',
            'category',
            'sales_type',
            'product_code',
            'self_price',
            'price',
            'sold_price',
            'status',
            'florist',
            'finished_at',
        )


class ProductFactoriesReportSummarySerializer(serializers.Serializer):
    total_finished_self_price = serializers.DecimalField(max_digits=19, decimal_places=2)
    total_finished_price = serializers.DecimalField(max_digits=19, decimal_places=2)
    total_finished_count = serializers.DecimalField(max_digits=19, decimal_places=2)
    total_sold_self_price = serializers.DecimalField(max_digits=19, decimal_places=2)
    total_sold_price = serializers.DecimalField(max_digits=19, decimal_places=2)
    total_sold_count = serializers.DecimalField(max_digits=19, decimal_places=2)
    total_written_off_self_price = serializers.DecimalField(max_digits=19, decimal_places=2)
    total_written_off_count = serializers.DecimalField(max_digits=19, decimal_places=2)
    total_product_count = serializers.DecimalField(max_digits=19, decimal_places=2)
    total_sale_sum = serializers.DecimalField(max_digits=19, decimal_places=2)


class ProductReturnsReportProductReturnListSerializer(serializers.ModelSerializer):
    order_name = serializers.CharField(source='order.__str__')
    price = serializers.DecimalField(source='order_item.price', max_digits=19, decimal_places=2)
    product = ProductSerializer(source='order_item.product', fields=('id', 'name', 'code'))
    created_user = UserSerializer()

    class Meta:
        model = OrderItemProductReturn
        fields = (
            'id',
            'order',
            'order_name',
            'product',
            'price',
            'count',
            'total',
            'total_self_price',
            'created_at',
            'created_user'
        )


class ProductReturnsReportProductFactoryReturnListSerializer(serializers.ModelSerializer):
    order_name = serializers.CharField(source='order.__str__')
    count = serializers.DecimalField(max_digits=19, decimal_places=2, default=1)
    total = serializers.DecimalField(source='price', max_digits=19, decimal_places=2)
    total_self_price = serializers.DecimalField(source='product_factory.self_price', max_digits=19, decimal_places=2)
    product_factory = ProductFactorySerializer(fields=('id', 'name', 'product_code'))
    returned_user = UserSerializer()

    class Meta:
        model = OrderItemProductFactory
        fields = (
            'id',
            'order',
            'order_name',
            'product_factory',
            'price',
            'count',
            'total',
            'total_self_price',
            'returned_at',
            'returned_user'
        )


class ProductReturnsReportSerializer(serializers.Serializer):
    total_product_returns = serializers.DecimalField(max_digits=19, decimal_places=2)
    total_product_returns_price = serializers.DecimalField(max_digits=19, decimal_places=2)
    total_product_returns_self_price = serializers.DecimalField(max_digits=19, decimal_places=2)
    total_product_factory_returns = serializers.DecimalField(max_digits=19, decimal_places=2)
    total_product_factory_returns_price = serializers.DecimalField(max_digits=19, decimal_places=2)
    total_product_factory_returns_self_price = serializers.DecimalField(max_digits=19, decimal_places=2)
    total_returns = serializers.DecimalField(max_digits=19, decimal_places=2)
    total_price = serializers.DecimalField(max_digits=19, decimal_places=2)
    total_self_price = serializers.DecimalField(max_digits=19, decimal_places=2)


class OrderItemsReportItemListSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name')
    product = ProductSerializer(fields=('id', 'name'))
    client_name = serializers.CharField(source='order.client.full_name')
    created_user = serializers.CharField(source='order.created_user.get_full_name')
    salesman_name = serializers.SerializerMethodField()
    industry = serializers.CharField(source='product.category.industry.name')
    order = OrderListSerializer(fields=('id',))
    total_discount = serializers.DecimalField(max_digits=19, decimal_places=2)
    total_charge = serializers.DecimalField(max_digits=19, decimal_places=2)
    total_self_price = serializers.DecimalField(max_digits=19, decimal_places=2)
    total_profit = serializers.DecimalField(max_digits=19, decimal_places=2)
    returned_count = serializers.DecimalField(max_digits=19, decimal_places=2)
    total = serializers.SerializerMethodField()
    article_id = serializers.IntegerField(source='id')

    class Meta:
        model = OrderItem
        fields = (
            'id',
            'order',
            'product',
            'product_name',
            'client_name',
            'salesman_name',
            'industry',
            'price',
            'count',
            'returned_count',
            'discount',
            'total',
            'total_discount',
            'total_charge',
            'total_self_price',
            'total_profit',
            'article_id',
            'created_user'
        )

    def get_total(self, obj):
        return str(decimal.Decimal(obj.total - obj.returned_total_sum))

    def get_salesman_name(self, obj):
        return obj.order.salesman.get_full_name() if obj.order.salesman else ""


class OrderItemsReportFactoryItemListSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product_factory.name')
    product = ProductFactorySerializer(fields=('id', 'name'), source='product_factory')
    client_name = serializers.CharField(source='order.client.full_name')
    salesman_name = serializers.SerializerMethodField()
    industry = serializers.CharField(source='product_factory.category.industry.name')
    order = OrderListSerializer(fields=('id',))
    total_discount = serializers.DecimalField(max_digits=19, decimal_places=2)
    total_charge = serializers.DecimalField(max_digits=19, decimal_places=2)
    total_self_price = serializers.DecimalField(max_digits=19, decimal_places=2)
    total_profit = serializers.DecimalField(max_digits=19, decimal_places=2)
    returned_count = serializers.DecimalField(max_digits=19, decimal_places=2)
    total = serializers.SerializerMethodField()
    article_id = serializers.IntegerField(default=0)
    created_user = serializers.CharField(source='order.created_user.get_full_name')

    class Meta:
        model = OrderItem
        fields = (
            'id',
            'order',
            'product',
            'product_name',
            'client_name',
            'salesman_name',
            'industry',
            'price',
            'count',
            'returned_count',
            'discount',
            'total',
            'total_discount',
            'total_charge',
            'total_self_price',
            'total_profit',
            'article_id',
            'created_user'
        )

    def get_total(self, obj):
        return str(decimal.Decimal(obj.total - obj.returned_total_sum))

    def get_salesman_name(self, obj):
        return obj.order.salesman.get_full_name() if obj.order.salesman else ""


class OrderItemsReportSerializer(serializers.Serializer):
    total_sum = serializers.DecimalField(max_digits=19, decimal_places=2)
    total_count_sum = serializers.DecimalField(max_digits=19, decimal_places=2)
    total_returned_count_sum = serializers.DecimalField(max_digits=19, decimal_places=2)
    total_discount_sum = serializers.DecimalField(max_digits=19, decimal_places=2)
    total_charge_sum = serializers.DecimalField(max_digits=19, decimal_places=2)
    total_self_price_sum = serializers.DecimalField(max_digits=19, decimal_places=2)
    total_profit_sum = serializers.DecimalField(max_digits=19, decimal_places=2)
    # total_returned_count_sum = serializers.DecimalField(max_digits=19, decimal_places=2)
    # total_returned_amount_sum = serializers.DecimalField(max_digits=19, decimal_places=2)
    # order_items = OrderItemsReportItemListSerializer(many=True)
    # factory_order_items = OrderItemsReportFactoryItemListSerializer(many=True)


class OverallReportSerializer(serializers.Serializer):
    total_sale_sum = serializers.DecimalField(max_digits=19, decimal_places=2)
    total_self_price_sum = serializers.DecimalField(max_digits=19, decimal_places=2)
    total_profit_sum = serializers.DecimalField(max_digits=19, decimal_places=2)
    total_debt_sum = serializers.DecimalField(max_digits=19, decimal_places=2)
    total_write_off_sum = serializers.DecimalField(max_digits=19, decimal_places=2)
    worker_incomes_sum = serializers.DecimalField(max_digits=19, decimal_places=2)
    outlay_total_sum = serializers.DecimalField(max_digits=19, decimal_places=2)
