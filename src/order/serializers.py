from decimal import Decimal

from django.utils import timezone
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from src.base.serializers import DynamicFieldsModelSerializer
from src.factory.enums import ProductFactoryStatus
from src.factory.models import ProductFactory
from src.factory.serializers import ProductFactorySerializer, ProductFactoryListSerializer
from src.order.enums import OrderStatus
from src.order.models import Client, Order, OrderItem, Department, OrderItemProductReturn, OrderItemProductFactory
from src.payment.models import PaymentMethod, Payment
from src.product.models import Product
from src.product.serializers import ProductSerializer, ProductListSerializer
from src.user.serializers import UserSerializer


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = 'id', 'name'


class ClientSerializer(DynamicFieldsModelSerializer):
    debt = serializers.DecimalField(max_digits=19, decimal_places=2, read_only=True)
    total_orders_sum = serializers.DecimalField(max_digits=19, decimal_places=2, read_only=True)

    class Meta:
        model = Client
        fields = 'id', 'full_name', 'phone_number', 'debt', 'comment', 'discount_percent', 'total_orders_sum'

    def validate_phone_number(self, value):
        if Client.objects.get_available().filter(phone_number=value).exists():
            raise serializers.ValidationError('Клиент с таким номером телфона уже существует')

        if value:
            if len(value) > 13:
                raise serializers.ValidationError("Неверный формат номера")
        return value


class ClientWithSummarySerializer(ClientSerializer):
    orders_count = serializers.DecimalField(max_digits=19, decimal_places=2, default=None)
    orders_count_in_year = serializers.DecimalField(max_digits=19, decimal_places=2, default=None)
    total_orders_sum = serializers.DecimalField(max_digits=19, decimal_places=2, default=None)
    total_orders_sum_in_year = serializers.DecimalField(max_digits=19, decimal_places=2, default=None)
    total_orders_profit_sum = serializers.DecimalField(max_digits=19, decimal_places=2, default=None)
    debt = serializers.DecimalField(max_digits=19, decimal_places=2, default=None)

    class Meta(ClientSerializer.Meta):
        model = Client
        fields = ClientSerializer.Meta.fields + (
            'orders_count',
            'orders_count_in_year',
            'total_orders_sum',
            'total_orders_sum_in_year',
            'total_orders_profit_sum',
            'debt',
        )


class OrderItemProductReturnSerializer(DynamicFieldsModelSerializer):
    created_user = UserSerializer(read_only=True)
    deleted_user = UserSerializer(read_only=True)
    product_name = serializers.CharField(read_only=True, source='order_item.product.name')

    class Meta:
        model = OrderItemProductReturn
        fields = (
            'id',
            'order',
            'order_item',
            'product_name',
            'count',
            'total',
            'total_self_price',
            'created_at',
            'created_user',
            'is_deleted',
            'deleted_user',
        )


class OrderItemProductFactoryReturnListSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product_factory.name', read_only=True)
    total = serializers.DecimalField(source='price', max_digits=19, decimal_places=2, read_only=True)
    count = serializers.DecimalField(max_digits=19, decimal_places=2, default=1, read_only=True)
    created_at = serializers.DateTimeField(source='returned_at', read_only=True)
    created_user = UserSerializer(source='returned_user', read_only=True)

    class Meta:
        model = OrderItemProductFactory
        fields = ('id', 'product_name', 'total', 'count', 'created_at', 'created_user')


class OrderItemProductFactoryReturnCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItemProductFactory
        fields = ('id',)

    def to_representation(self, instance):
        return OrderItemProductFactoryReturnListSerializer(instance=instance).data


class OrderListSerializer(DynamicFieldsModelSerializer):
    client = ClientSerializer(read_only=True)
    department = DepartmentSerializer(read_only=True)
    created_user = UserSerializer(read_only=True)
    salesman = UserSerializer(read_only=True)
    total_with_discount = serializers.DecimalField(
        read_only=True,
        max_digits=19,
        decimal_places=2,
        source='get_total_with_discount'
    )
    client_name = serializers.SerializerMethodField(read_only=True)
    discount = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = (
            'id',
            'client_name',
            'client',
            'department',
            'status',
            'discount',
            'total',
            'total_with_discount',
            'debt',
            'created_at',
            'salesman',
            'created_user',
            'comment'
        )

    def get_client_name(self, obj):
        return obj.client.full_name

    def get_discount(self, obj):
        return str(obj.discount + obj.products_discount)


class OrderListSummarySerializer(serializers.Serializer):
    total_sale_with_discount_amount = serializers.DecimalField(max_digits=19, decimal_places=2, read_only=True)
    total_discount_amount = serializers.DecimalField(max_digits=19, decimal_places=2, read_only=True)
    total_charge_amount = serializers.DecimalField(max_digits=19, decimal_places=2, read_only=True)
    total_self_price_amount = serializers.DecimalField(max_digits=19, decimal_places=2, read_only=True)
    total_profit_amount = serializers.DecimalField(max_digits=19, decimal_places=2, read_only=True)
    total_debt_amount = serializers.DecimalField(max_digits=19, decimal_places=2, read_only=True)
    created_orders_count = serializers.IntegerField(read_only=True)


class OrderItemListSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    returned_count = serializers.DecimalField(max_digits=19, decimal_places=2)
    returns = OrderItemProductReturnSerializer(many=True, read_only=True, source='product_returns')
    total = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = OrderItem
        fields = 'id', 'product', 'price', 'count', 'total', 'returned_count', 'returns'

    def get_total(self, obj):
        return str(Decimal(obj.total - obj.returned_total_sum))


class OrderItemProductFactorySerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItemProductFactory
        fields = ('id', 'order', 'product_factory', 'price')


class OrderItemProductFactoryListSerializer(OrderItemProductFactorySerializer):
    product_factory = ProductFactoryListSerializer(
        fields=('id', 'name', 'product_code', 'price', 'self_price', 'status', 'florist')
    )
    total = serializers.SerializerMethodField()
    count = serializers.DecimalField(max_digits=19, decimal_places=2, default=1)

    class Meta(OrderItemProductFactorySerializer.Meta):
        model = OrderItemProductFactory
        fields = OrderItemProductFactorySerializer.Meta.fields + ('total', 'count', 'is_returned')

    def get_total(self, obj):
        return str(Decimal(obj.price if not obj.is_returned else 0))


class OrderPaymentMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentMethod
        fields = ('id', 'name',)


class OrderPaymentListSerializer(DynamicFieldsModelSerializer):
    created_user = UserSerializer()

    payment_method = OrderPaymentMethodSerializer(read_only=True)

    class Meta:
        model = Payment
        fields = (
            'id',
            'payment_method',
            'payment_type',
            'amount',
            'created_at',
            'created_user',
            'comment'
        )


class OrderDetailSerializer(OrderListSerializer):
    client = ClientWithSummarySerializer(read_only=True)
    order_items = OrderItemListSerializer(many=True)
    order_item_factory_products = OrderItemProductFactoryListSerializer(
        many=True,
        source='order_item_product_factory_set',
    )
    # product_returns = OrderItemProductReturnSerializer(many=True)
    factory_product_returns = serializers.SerializerMethodField()
    amount_paid = serializers.DecimalField(read_only=True, source='get_amount_paid', max_digits=19, decimal_places=2)
    amount_returned = serializers.DecimalField(
        read_only=True,
        source='get_amount_money_returned',
        max_digits=19,
        decimal_places=2
    )
    payments = OrderPaymentListSerializer(
        read_only=True,
        many=True,
        fields=(
            'id', 'amount', 'payment_method', 'payment_type', 'created_at', 'created_user', 'comment'
        )
    )

    class Meta(OrderListSerializer.Meta):
        fields = OrderListSerializer.Meta.fields + (
            'amount_paid',
            'amount_returned',
            'order_items',
            # 'product_returns',
            'factory_product_returns',
            'order_item_factory_products',
            'payments',
        )

    def get_factory_product_returns(self, obj: Order):
        returned_items = obj.order_item_product_factory_set.filter(is_returned=True).select_related('returned_user')
        return OrderItemProductFactoryReturnListSerializer(
            data=returned_items, many=True
        ).to_representation(returned_items)


class OrderItemProductFactoryCreateSerializer(OrderItemProductFactorySerializer):
    product_factory = serializers.PrimaryKeyRelatedField(required=False, queryset=ProductFactory.objects.all())
    code = serializers.CharField(required=False)

    class Meta(OrderItemProductFactorySerializer.Meta):
        model = OrderItemProductFactory
        fields = OrderItemProductFactorySerializer.Meta.fields + ('code',)
        read_only_fields = ('order', 'price')

    def validate(self, data):
        product = data.get('product_factory')
        code = data.get('code')
        if not code and not product:
            raise serializers.ValidationError("Необходимо указать id либо штрих-код товара")
        return data

    def validate_product_factory(self, value):
        if value.is_deleted:
            raise ValidationError("Товар удален и не может быть добавлен к заказу.")
        if value.status == ProductFactoryStatus.CREATED:
            raise ValidationError("Товар еще не завершен и не может быть добавлен к заказу.")
        if value.status == ProductFactoryStatus.SOLD:
            raise ValidationError("Товар уже продан и не может быть добавлен к заказу.")
        if value.status == ProductFactoryStatus.SOLD:
            raise ValidationError("Товар находится в ожидании разборки и не может быть добавлен к заказу.")
        return value

    # def to_representation(self, instance):
    #
    #     return {
    #         **OrderItemProductFactoryListSerializer(instance=instance).data,
    #         "order": OrderDetailSerializer(instance=instance.order, fields=(
    #             'id',
    #             'amount_paid',
    #             'total',
    #             'total_with_discount',
    #             'discount',
    #         )).data
    #     }


class OrderItemProductFactoryUpdateSerializer(OrderItemProductFactorySerializer):
    class Meta(OrderItemProductFactorySerializer.Meta):
        model = OrderItemProductFactory
        read_only_fields = ('order', 'product_factory')

    # def to_representation(self, instance):
    #     return {
    #         **super().to_representation(instance),
    #         "order": OrderDetailSerializer(instance=instance.order, fields=(
    #             'id',
    #             'amount_paid',
    #             'total',
    #             'total_with_discount',
    #             'discount',
    #         )).data
    #     }


class OrderItemCreateSerializer(serializers.ModelSerializer):
    code = serializers.CharField(required=False)
    product = serializers.PrimaryKeyRelatedField(required=False, queryset=Product.objects.all())

    class Meta:
        model = OrderItem
        fields = 'id', 'product', 'code', 'count', 'price', 'total'
        read_only_fields = 'id', 'price', 'total'

    def validate(self, data):
        code = data.get('code')
        product = data.get('product')
        if not code and not product:
            raise serializers.ValidationError("Необходимо указать id либо штрих-код товара")
        return data

    # def to_representation(self, instance):
    #     from src.product.models import Product
    #     product = Product.objects.with_in_stock().get(pk=instance.product_id)
    #     return {
    #         **super().to_representation(instance),
    #         "product": ProductListSerializer(instance=product, fields=('id', 'in_stock')).data,
    #         "order": OrderDetailSerializer(instance=instance.order, fields=(
    #             'id',
    #             'amount_paid',
    #             'total',
    #             'total_with_discount',
    #             'discount'
    #         )).data
    #     }


class OrderItemUpdateSerializer(serializers.ModelSerializer):
    order = OrderDetailSerializer(fields=(
        'id',
        'amount_paid',
        'total',
        'total_with_discount',
        # 'discount',
    ))
    product = ProductListSerializer(fields=('id', 'in_stock'))

    class Meta:
        model = OrderItem
        depth = 1
        fields = 'id', 'product', 'count', 'price', 'total', 'order'
        read_only_fields = 'product', 'total', 'order'


class OrderCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = 'client', 'salesman', 'department', 'comment',
        extra_kwargs = {'discount': {'required': False}, 'department': {'required': True}}

    # def to_representation(self, instance):
    #     return OrderDetailSerializer(instance=self.instance, exclude=('order_items',)).data


class OrderUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = 'client', 'salesman', 'department', 'comment', 'created_at'
        extra_kwargs = {'created_at': {'read_only': False}}

    def validate_created_at(self, value):
        if value > timezone.now():
            raise ValidationError("Дата создания не может быть в будущем")
        return value

    # def to_representation(self, instance):
    #     return OrderDetailSerializer(instance=self.instance, exclude=('order_items',)).data


class PaymentMethodListSerializer(serializers.Serializer):
    id = serializers.PrimaryKeyRelatedField(required=True, queryset=PaymentMethod.objects.all())
    amount = serializers.DecimalField(max_digits=19, decimal_places=2, default=0)


class OrderCompleteSerializer(serializers.Serializer):
    payments = PaymentMethodListSerializer(many=True, required=False)


class OrderUpdateStatusSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=OrderStatus.choices)


class OrderUpdateTotalSerializer(serializers.Serializer):
    discount = serializers.DecimalField(max_digits=19, decimal_places=2)


class OrderItemProductReturnCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItemProductReturn
        fields = ('id', 'count')
