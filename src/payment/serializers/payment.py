import datetime

from django.utils import timezone
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from src.base.exceptions import BusinessLogicException
from src.base.serializers import DynamicFieldsModelSerializer
from src.income.models import Provider, Income
from src.income.serializers import IncomeListSerializer, ProviderSerializer
from src.order.models import Order
# from src.order.serializers import OrderListSerializer, ClientSerializer
from src.payment.enums import OutlayType
from src.payment.models import Payment, Outlay, PaymentMethodCategory, PaymentMethod
from src.user.serializers import UserSerializer


class PaymentMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentMethod
        fields = ('id', 'name', 'is_active')


class PaymentMethodCategorySerializer(serializers.ModelSerializer):
    payment_methods = PaymentMethodSerializer(many=True)

    class Meta:
        model = PaymentMethodCategory
        fields = ('id', 'name', 'payment_methods')


class PaymentListSerializer(DynamicFieldsModelSerializer):
    from src.order.serializers import OrderListSerializer, ClientSerializer

    created_user = UserSerializer()
    order = OrderListSerializer(read_only=True, fields=('id',))
    client = ClientSerializer(read_only=True, fields=('id', 'full_name'))
    income = IncomeListSerializer(read_only=True, fields=('id',))
    provider = ProviderSerializer(read_only=True, fields=('id', 'full_name'))
    worker = UserSerializer(read_only=True)
    payment_method = PaymentMethodSerializer(read_only=True)

    from src.payment.serializers.outlay import OutlayListSerializer
    outlay = OutlayListSerializer(read_only=True, fields=('id', 'title'))

    class Meta:
        model = Payment
        fields = (
            'id',
            'payment_method',
            'payment_type',
            'payment_model_type',
            'amount',
            'income',
            'order',
            'provider',
            'client',
            'worker',
            'outlay',
            'created_at',
            'created_user',
            'comment',
            'is_debt'
        )


class PaymentSummaryListSerializer(serializers.Serializer):
    total_income = serializers.DecimalField(read_only=True, max_digits=19, decimal_places=2)
    total_outcome = serializers.DecimalField(read_only=True, max_digits=19, decimal_places=2)
    total_profit = serializers.DecimalField(read_only=True, max_digits=19, decimal_places=2)
    total_count = serializers.DecimalField(read_only=True, max_digits=19, decimal_places=2)
    payments = PaymentListSerializer(read_only=True, many=True)


class PaymentCreateSerializer(serializers.ModelSerializer):
    # created_user = UserSerializer(read_only=True)

    class Meta:
        model = Payment
        fields = (
            'id',
            'payment_method',
            'payment_type',
            'payment_model_type',
            'amount',
            'comment',
            'created_at',
            'created_user'
        )
        read_only_fields = ('created_at', 'created_user', 'payment_model_type')


class PaymentUpdateSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(read_only=False)

    class Meta:
        model = Payment
        fields = (
            'payment_method',
            'payment_type',
            'amount',
            'comment',
            'created_at',
            'created_user'
        )

    def validate_created_at(self, value):
        if value > timezone.now():
            raise ValidationError("Дата создания не может быть в будущем")
        return value

    def update(self, instance: Order, validated_data):
        created_at = validated_data.pop('created_at', None)
        if created_at:
            created_at = datetime.datetime.combine(created_at.date(), instance.created_at.time())
            instance.created_at = created_at
            # if instance.order and created_at < instance.order.created_at:
            #     raise BusinessLogicException("Дата создания платежа не может быть раньше даты создания заказа")
            # if instance.income and created_at < instance.income.created_at:
            #     raise BusinessLogicException("Дата создания платежа не может быть раньше даты создания прихода")
        return super().update(instance, validated_data)


class OutlayPaymentCreateSerializer(PaymentCreateSerializer):
    item = serializers.PrimaryKeyRelatedField(
        label='Расход',
        queryset=Outlay.objects.all(),
        required=True,
        allow_null=False,
        source='outlay'
    )

    class Meta(PaymentCreateSerializer.Meta):
        model = Payment
        fields = PaymentCreateSerializer.Meta.fields + ('item', 'worker')

    def validate(self, data):
        outlay = data.get('outlay')
        worker = data.get('worker')
        if outlay.outlay_type == OutlayType.WORKERS and not worker:
            raise serializers.ValidationError("Необходимо указать сотрудника")
        return data


class OrderPaymentCreateSerializer(PaymentCreateSerializer):
    item = serializers.PrimaryKeyRelatedField(
        label='Заказ',
        queryset=Order.objects.all(),
        required=True,
        allow_null=False,
        source='order'
    )

    class Meta(PaymentCreateSerializer.Meta):
        model = Payment
        fields = PaymentCreateSerializer.Meta.fields + ('item',)


class IncomePaymentCreateSerializer(PaymentCreateSerializer):
    item = serializers.PrimaryKeyRelatedField(
        label='Приход',
        queryset=Income.objects.all(),
        required=True,
        allow_null=False,
        source='income'
    )

    class Meta(PaymentCreateSerializer.Meta):
        model = Payment
        fields = PaymentCreateSerializer.Meta.fields + ('item',)


class ProviderPaymentCreateSerializer(PaymentCreateSerializer):
    item = serializers.PrimaryKeyRelatedField(
        label='Поставщик',
        queryset=Provider.objects.all(),
        required=True,
        allow_null=False,
        source='provider'
    )

    class Meta(PaymentCreateSerializer.Meta):
        model = Payment
        fields = PaymentCreateSerializer.Meta.fields + ('item',)
