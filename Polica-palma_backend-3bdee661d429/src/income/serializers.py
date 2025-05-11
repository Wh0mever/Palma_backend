from decimal import Decimal

from rest_framework import serializers

from src.base.serializers import DynamicFieldsModelSerializer
from src.product.serializers import ProductSerializer
from src.income.models import Provider, Income, IncomeItem
from src.income.enums import IncomeStatus
from src.user.serializers import UserSerializer


class ProviderSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = Provider
        fields = 'id', 'full_name', 'phone_number', 'org_name', 'balance', 'comment'
        read_only_fields = 'balance',


class IncomeItemSerializer(DynamicFieldsModelSerializer):
    product = ProductSerializer(read_only=True)
    last_price = serializers.DecimalField(source='get_last_price', read_only=True, max_digits=19, decimal_places=2)
    last_sale_price = serializers.DecimalField(source='get_last_sale_price', read_only=True, max_digits=19,
                                               decimal_places=2)

    # sale_price = serializers.DecimalField(source='product.price', read_only=True, max_digits=19, decimal_places=2)

    class Meta:
        model = IncomeItem
        fields = 'id', 'product', 'count', 'price', 'sale_price', 'total', 'total_sale_price', 'last_price', \
            'last_sale_price'
        read_only_fields = 'total', 'total_sale_price'


class IncomeItemCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = IncomeItem
        fields = 'id', 'product', 'count', 'price', 'sale_price', 'total', 'total_sale_price'
        read_only_fields = 'total', 'total_sale_price'


class IncomeItemMultipleCreateSerializer(serializers.Serializer):
    income_items = IncomeItemCreateSerializer(many=True)


class IncomeItemUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = IncomeItem
        fields = 'id', 'product', 'count', 'price', 'sale_price', 'total', 'total_sale_price'
        read_only_fields = 'total', 'product', 'total_sale_price'


class IncomeItemMultipleUpdateItemSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    count = serializers.DecimalField(allow_null=True, max_digits=19, decimal_places=2)
    price = serializers.DecimalField(allow_null=True, max_digits=19, decimal_places=2)
    sale_price = serializers.DecimalField(allow_null=True, max_digits=19, decimal_places=2)

    class Meta:
        model = IncomeItem
        fields = 'id', 'product', 'count', 'price', 'sale_price', 'total', 'total_sale_price'
        read_only_fields = 'total', 'product', 'total_sale_price'


class IncomeItemMultipleUpdateSerializer(serializers.Serializer):
    income_items = IncomeItemMultipleUpdateItemSerializer(many=True)


class IncomeListSerializer(DynamicFieldsModelSerializer):
    provider = ProviderSerializer(read_only=True)
    created_user = UserSerializer(read_only=True)
    provider_name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Income
        fields = 'id', 'provider_name', 'provider', 'total', 'total_sale_price', \
            'status', 'comment', 'created_at', 'created_user'

    def get_provider_name(self, obj):
        return obj.provider.full_name


class IncomeListSummarySerializer(serializers.Serializer):
    total_sum = serializers.DecimalField(max_digits=19, decimal_places=2)
    total_count = serializers.DecimalField(max_digits=19, decimal_places=2)


class IncomeDetailSerializer(IncomeListSerializer):
    income_items = IncomeItemSerializer(many=True, read_only=True, source="income_item_set")

    class Meta(IncomeListSerializer.Meta):
        fields = IncomeListSerializer.Meta.fields + ('income_items',)


class IncomeCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Income
        fields = 'id', 'provider', 'comment', 'total', 'total_sale_price', 'status', 'created_at', 'created_user'
        read_only_fields = 'total', 'total_sale_price', 'status', 'created_at', 'created_user'


class IncomeUpdateStatusSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=IncomeStatus.choices)
