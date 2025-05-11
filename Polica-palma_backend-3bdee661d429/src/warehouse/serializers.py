from rest_framework import serializers

from src.base.serializers import DynamicFieldsModelSerializer
from src.product.serializers import ProductSerializer
from src.user.serializers import UserSerializer
from src.warehouse.models import WarehouseProduct, WarehouseProductWriteOff


class WarehouseProductSerializer(DynamicFieldsModelSerializer):
    product = ProductSerializer()
    product_name = serializers.SerializerMethodField(read_only=True)

    # sale_price = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = WarehouseProduct
        fields = ('id', 'product_name', 'product', 'count', 'sale_price', 'self_price', 'created_at')

    def get_product_name(self, obj):
        return obj.product.name

    # def get_sale_price(self, obj):
    #     return str(obj.product.price)


class WarehouseProductSummarySerializer(serializers.Serializer):
    total_self_price_sum = serializers.DecimalField(max_digits=19, decimal_places=2, default=0)


class WarehouseProductWriteOffSerializer(serializers.ModelSerializer):
    warehouse_product = WarehouseProductSerializer()
    product_name = serializers.SerializerMethodField()
    created_user = UserSerializer()
    deleted_user = UserSerializer()

    class Meta:
        model = WarehouseProductWriteOff
        fields = (
            'id',
            'warehouse_product',
            'product_name',
            'count',
            'comment',
            'created_at',
            'created_user',
            'is_deleted',
            'deleted_user'
        )

    def get_product_name(self, obj):
        return obj.warehouse_product.product.name


class WarehouseProductWriteOffCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = WarehouseProductWriteOff
        fields = (
            'id',
            'warehouse_product',
            'count',
            'comment',
        )

    def to_representation(self, instance):
        return WarehouseProductWriteOffSerializer(instance=instance).data
