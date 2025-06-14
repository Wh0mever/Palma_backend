from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from src.base.serializers import DynamicFieldsModelSerializer
from src.income.models import ProviderProduct, Provider, IncomeItem
from src.product.enums import ProductUnitType
from src.product.models import Product, Industry, Category


class IndustrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Industry
        fields = 'id', 'name', 'sale_compensation_percent', 'has_sale_compensation'


class ProductCreateSerializer(serializers.ModelSerializer):
    image = Base64ImageField(required=False)
    provider = serializers.PrimaryKeyRelatedField(required=False, queryset=Provider.objects.all())

    class Meta:
        model = Product
        fields = 'id', 'name', 'unit_type', 'code', 'category', 'price', 'provider', 'image'


class CategorySerializer(serializers.ModelSerializer):
    industry = IndustrySerializer()

    class Meta:
        model = Category
        fields = 'id', 'name', 'industry', 'is_composite', 'is_for_sale'


class CategoryCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = 'id', 'name', 'industry', 'is_composite', 'is_for_sale'

    def to_representation(self, instance):
        return CategorySerializer(instance=instance).data


class ProductSerializer(DynamicFieldsModelSerializer):
    category = CategorySerializer(read_only=True)
    is_product_factory = serializers.BooleanField(read_only=True, default=False)
    is_barcode_printable = serializers.BooleanField(read_only=True)

    class Meta:
        model = Product
        fields = (
            'id',
            'name',
            'unit_type',
            'code',
            'price',
            'category',
            'image',
            'is_product_factory',
            'is_barcode_printable'
        )
        read_only_fields = 'code',


class ProductListSerializer(ProductSerializer):
    in_stock = serializers.DecimalField(max_digits=19, decimal_places=2)

    class Meta(ProductSerializer.Meta):
        model = Product
        fields = ProductSerializer.Meta.fields + ('in_stock',)
        read_only_fields = ProductSerializer.Meta.read_only_fields + ('in_stock',)


class ProductDetailSerializer(ProductListSerializer):
    from src.income.serializers import ProviderSerializer

    in_stock = serializers.DecimalField(max_digits=19, decimal_places=2)
    related_providers = ProviderSerializer(many=True)

    class Meta(ProductSerializer.Meta):
        model = Product
        fields = ProductSerializer.Meta.fields + ('in_stock', 'related_providers')
        read_only_fields = ProductSerializer.Meta.read_only_fields + ('in_stock', 'related_providers')

    def to_representation(self, instance):
        instance.related_providers = Provider.objects.filter(products__in=instance.providers.all())
        return super().to_representation(instance)


class ProductIncomeItemSerializer(DynamicFieldsModelSerializer):
    created_at = serializers.DateTimeField(source='income.created_at')

    class Meta:
        model = IncomeItem
        fields = ('id', 'count', 'price', 'sale_price', 'total', 'created_at')


class ProductIncomeHistorySerializer(ProductListSerializer):
    income_items = ProductIncomeItemSerializer(many=True)

    class Meta:
        model = Product
        fields = ('id', 'name', 'income_items')


class ProductCompositeListSerializer(ProductListSerializer):
    from src.warehouse.serializers import WarehouseProductSerializer
    warehouse_products = WarehouseProductSerializer(
        many=True,
        read_only=True,
        exclude=('product', 'product_name')
    )

    class Meta(ProductListSerializer.Meta):
        model = Product
        fields = ProductListSerializer.Meta.fields + ('warehouse_products',)


class CategoryDetailSerializer(CategorySerializer):
    products = ProductSerializer(many=True, read_only=True, source="product_set")

    class Meta(CategorySerializer.Meta):
        fields = CategorySerializer.Meta.fields + ('products',)


class IndustryDetailSerializer(IndustrySerializer):
    categories = CategorySerializer(many=True, read_only=True, source="category_set")

    class Meta(IndustrySerializer.Meta):
        fields = IndustrySerializer.Meta.fields + ('categories',)


class ProductOptionsSerializer(serializers.ModelSerializer):
    unit_types = serializers.ChoiceField(choices=ProductUnitType.choices, source='unit_type')

    class Meta:
        model = Product
        fields = 'unit_types',


class AddDeleteProviderSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProviderProduct
        fields = ('id', 'provider')
