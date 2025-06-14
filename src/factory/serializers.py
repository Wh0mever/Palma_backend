from django.db import models
from django.contrib.auth import get_user_model
from django.db.models import Q
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from src.base.serializers import DynamicFieldsModelSerializer
from src.factory.models import ProductFactory, ProductFactoryItem, ProductFactoryCategory, ProductFactoryItemReturn
from src.product.serializers import IndustrySerializer
from src.user.enums import UserType
from src.user.serializers import UserSerializer
from src.warehouse.serializers import WarehouseProductSerializer

User = get_user_model()


class ProductFactoryCategorySerializer(DynamicFieldsModelSerializer):
    industry = IndustrySerializer()

    class Meta:
        model = ProductFactoryCategory
        fields = ('id', 'name', 'industry', 'charge_percent')


class ProductFactoryCategoryCreateSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = ProductFactoryCategory
        fields = ('id', 'name', 'industry', 'charge_percent')


class ProductFactoryItemReturnSerializer(serializers.ModelSerializer):
    created_user = UserSerializer(read_only=True)
    deleted_user = UserSerializer(read_only=True)

    class Meta:
        model = ProductFactoryItemReturn
        fields = (
            'id',
            'count',
            'total_self_price',
            'total_price',
            'created_at',
            'created_user',
            'is_deleted',
            'deleted_user'
        )
        read_only_fields = (
            'total_self_price',
            'total_price',
            'created_at',
            'created_user',
            'is_deleted',
            'deleted_user'
        )


class ProductFactoryItemReturnCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductFactoryItemReturn
        fields = (
            'id',
            'count',
            'total_self_price',
            'total_price',
            'created_at',
            'created_user',
        )
        read_only_fields = (
            'total_self_price',
            'total_price',
            'created_at',
            'created_user',
        )


class ProductFactorySerializer(DynamicFieldsModelSerializer):
    is_product_factory = serializers.BooleanField(read_only=True, default=True)

    class Meta:
        model = ProductFactory
        fields = (
            'id',
            'name',
            'product_code',
            'category',
            'image',
            'price',
            'self_price',
            'status',
            'sales_type',
            'florist',
            'created_at',
            'created_user',
            'finished_at',
            'finished_user',
            'is_deleted',
            'deleted_user',
            'written_off_at',
            'is_product_factory',
        )
        read_only_fields = (
            'product_code',
            'self_price',
            'status',
            'created_at',
            'created_user',
            'finished_at',
            'finished_user',
            'written_off_at',
            'is_deleted',
            'deleted_user'
        )


class ProductFactoryListSerializer(ProductFactorySerializer):
    category = ProductFactoryCategorySerializer(read_only=True)
    florist = UserSerializer(read_only=True)
    created_user = UserSerializer(read_only=True)
    finished_user = UserSerializer(read_only=True)
    deleted_user = UserSerializer(read_only=True)

    class Meta(ProductFactorySerializer.Meta):
        model = ProductFactory


class ProductFactoryFinishedListSerializer(ProductFactoryListSerializer):
    in_stock = serializers.IntegerField(default=1)

    class Meta(ProductFactoryListSerializer.Meta):
        model = ProductFactory
        fields = ProductFactoryListSerializer.Meta.fields + ('in_stock',)


class ProductFactorySummarySerializer(serializers.Serializer):
    total_sale_price_sum = serializers.IntegerField(default=0)
    total_self_price_sum = serializers.IntegerField(default=0)
    total_profit_sum = serializers.IntegerField(default=0)
    total_count = serializers.IntegerField(default=0)


class ProductFactoryWrittenOffSummarySerializer(serializers.Serializer):
    total_self_price = serializers.DecimalField(max_digits=19, decimal_places=2, default=0)
    total_count = serializers.IntegerField(default=0)


class ProductFactoryCreateSerializer(ProductFactorySerializer):
    image = Base64ImageField(required=False)
    florist = serializers.PrimaryKeyRelatedField(required=False, queryset=User.objects.filter(is_active=True))

    class Meta(ProductFactorySerializer.Meta):
        model = ProductFactory
        read_only_fields = ProductFactorySerializer.Meta.read_only_fields + ('price', 'name')

    def validate_florist(self, value):
        if value.type not in [UserType.FLORIST, UserType.FLORIST_PERCENT, UserType.CRAFTER, UserType.FLORIST_ASSISTANT]:
            raise serializers.ValidationError("Пользователь не является флористом")
        return value


class ProductFactoryItemSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = ProductFactoryItem
        fields = ('id', 'factory', 'warehouse_product', 'count', 'total_price', 'total_self_price')
        read_only_fields = ('factory', 'total_price', 'total_self_price')


class ProductFactoryItemDetailSerializer(ProductFactoryItemSerializer):
    warehouse_product = WarehouseProductSerializer()
    returns = ProductFactoryItemReturnSerializer(many=True, read_only=True, source='product_returns')
    returned_count = serializers.SerializerMethodField()

    class Meta(ProductFactoryItemSerializer.Meta):
        model = ProductFactoryItem
        fields = ProductFactoryItemSerializer.Meta.fields + ('returns', 'returned_count')

    def get_returned_count(self, obj):
        return ProductFactoryItemReturn.objects.filter(factory_item=obj, is_deleted=False) \
            .aggregate(count_sum=models.Sum('count', default=0))['count_sum']


class ProductFactoryItemCreateSerializer(ProductFactoryItemSerializer):
    class Meta(ProductFactoryItemSerializer.Meta):
        model = ProductFactoryItem

    def to_representation(self, instance):
        return ProductFactoryItemDetailSerializer(instance=instance).data


class ProductFactoryItemUpdateSerializer(ProductFactoryItemSerializer):
    class Meta(ProductFactoryItemSerializer.Meta):
        model = ProductFactoryItem
        read_only_fields = ProductFactoryItemSerializer.Meta.read_only_fields + ('warehouse_product',)


class ProductFactoryItemWriteOffSerializer(ProductFactoryItemSerializer):
    write_off_count = serializers.DecimalField(max_digits=19, decimal_places=2, required=True, write_only=True)

    class Meta(ProductFactoryItemSerializer.Meta):
        model = ProductFactoryItem
        fields = ProductFactoryItemSerializer.Meta.fields + ('write_off_count',)
        read_only_fields = ProductFactoryItemSerializer.Meta.read_only_fields + ('warehouse_product', 'count')


class ProductFactoryDetailSerializer(ProductFactorySerializer):
    category = ProductFactoryCategorySerializer(read_only=True)
    florist = UserSerializer(read_only=True)
    created_user = UserSerializer(read_only=True)
    finished_user = UserSerializer(read_only=True)
    deleted_user = UserSerializer(read_only=True)
    items = ProductFactoryItemDetailSerializer(source='product_factory_item_set', many=True, read_only=True)
    sold_user = serializers.SerializerMethodField()
    order = serializers.SerializerMethodField()

    class Meta(ProductFactorySerializer.Meta):
        model = ProductFactory
        fields = ProductFactorySerializer.Meta.fields + ('items', 'sold_user', 'order')

    def get_sold_user(self, obj: ProductFactory):
        from src.order.models import Order
        order = Order.objects.get_available().filter(~Q(status="CANCELLED")).filter(
            order_item_product_factory_set__product_factory=obj
        ).distinct().first()
        if order:
            serializer = UserSerializer(instance=order.salesman)
            return serializer.data
        return None

    def get_order(self, obj: ProductFactory):
        from src.order.models import Order
        from src.order.serializers import OrderListSerializer
        order = Order.objects.get_available().filter(~Q(status="CANCELLED")).filter(
            order_item_product_factory_set__product_factory=obj
        ).distinct().first()
        if order:
            serializer = OrderListSerializer(instance=order, fields=('id',))
            return serializer.data
        return None


class ProductFactoryFinishSerializer(serializers.ModelSerializer):
    # finished_user = UserSerializer(read_only=True)

    class Meta:
        model = ProductFactory
        fields = ('id', 'price', 'status', 'finished_at', 'finished_user')
        read_only_fields = ('price', 'status', 'finished_at', 'finished_user')

# class ProductFactoryCancelSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = ProductFactory
#         fields = ('id', 'status')
#
#
# class ProductFactoryWriteOffSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = ProductFactory
#         fields = ('id', 'status')
