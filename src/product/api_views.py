from django.db import models, IntegrityError
from django.utils.decorators import method_decorator
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from rest_framework import filters
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from src.base.api_views import MultiSerializerViewSetMixin, DestroyFlagsViewSetMixin, CustomPagination
from src.income.enums import IncomeStatus
from src.income.models import ProviderProduct, IncomeItem
from src.product.enums import ProductUnitType
from src.product.filters import ProductFilter
from src.product.helpers import generate_product_code
from src.product.models import Industry, Category, Product
from src.product.serializers import IndustrySerializer, CategorySerializer, IndustryDetailSerializer, \
    CategoryDetailSerializer, ProductCreateSerializer, ProductListSerializer, \
    CategoryCreateSerializer, ProductCompositeListSerializer, AddDeleteProviderSerializer, ProductDetailSerializer, \
    ProductIncomeHistorySerializer
from src.product.services import delete_industry, delete_category
from src.user.enums import UserType
from src.warehouse.models import WarehouseProduct


class IndustryViewSet(MultiSerializerViewSetMixin, ModelViewSet):
    queryset = Industry.objects.get_available()
    serializer_class = IndustrySerializer
    serializer_action_classes = {
        'retrieve': IndustryDetailSerializer,
        'partial_update': IndustrySerializer,
    }

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.by_user_industry(self.request.user)
        return qs

    def perform_destroy(self, instance):
        delete_industry(instance)


class CategoryViewSet(MultiSerializerViewSetMixin, ModelViewSet):
    queryset = Category.objects.get_available().select_related('industry')
    serializer_class = CategorySerializer
    serializer_action_classes = {
        'retrieve': CategoryDetailSerializer,
        'create': CategoryCreateSerializer,
        'partial_update': CategoryCreateSerializer,
    }

    def get_queryset(self):
        qs = super().get_queryset()
        if self.action in ['list'] and self.request.user.type == UserType.MANAGER:
            qs = qs.filter(industry__is_deleted=False).by_user_industry(self.request.user)

        return qs

    def perform_destroy(self, instance):
        delete_category(instance)

    def composite_list(self, request, *args, **kwargs):
        qs = self.get_queryset()
        qs = qs.filter(is_composite=True)
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data, status=200)

    def for_sale_list(self, request):
        qs = self.get_queryset()
        qs = qs.filter(is_for_sale=True)
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data, status=200)


@method_decorator(name="create", decorator=swagger_auto_schema(
    request_body=ProductCreateSerializer()
))
class ProductViewSet(MultiSerializerViewSetMixin, DestroyFlagsViewSetMixin, ModelViewSet):
    queryset = Product.objects.get_available().select_related('category')
    serializer_class = ProductListSerializer
    serializer_action_classes = {
        'retrieve': ProductDetailSerializer,
        'create': ProductCreateSerializer,
        'partial_update': ProductCreateSerializer,
        'add_provider': AddDeleteProviderSerializer,
        'delete_provider': AddDeleteProviderSerializer,
        'get_product_income_history': ProductIncomeHistorySerializer,
    }
    filter_backends = [
        filters.SearchFilter,
        DjangoFilterBackend,
    ]
    filterset_class = ProductFilter
    pagination_class = CustomPagination
    search_fields = ['name', 'code']

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.prefetch_related('warehouse_products', 'category__industry', 'income_items')
        qs = qs.get_available().with_in_stock()
        if self.action != "get_for_sale_products" and self.request.user.type != UserType.SALESMAN:
            qs = qs.by_user_industry(self.request.user)
        qs = qs.order_by('id')
        return qs

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        code = data.get('code')
        provider = data.pop('provider', None)
        try:
            if code:
                product = serializer.save(code=code)
            else:
                product = serializer.save()
                code = generate_product_code(product)
                product.code = code
                product.save()
            if provider:
                ProviderProduct.objects.create(product=product, provider=provider)
        except IntegrityError:
            return Response(data={"error": "Этот штрих-код уже использован"}, status=400)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=201, headers=headers)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        code = data.get('code', None)
        try:
            if not code and not instance.code:
                code = generate_product_code(instance)
                serializer.save(code=code)
            else:
                serializer.save()
        except IntegrityError:
            return Response(data={"error": "Этот штрих-код уже использован"}, status=400)
        return Response(serializer.data)

    def get_for_sale_products(self, request):
        queryset = self.filter_queryset(self.get_queryset()).filter(category__is_for_sale=True)

        class SpecificActionPagination(CustomPagination):
            page_size = 9

        paginator = SpecificActionPagination()
        page = paginator.paginate_queryset(queryset, request, view=self)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def add_provider(self, request, *args, **kwargs):
        product = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            serializer.save(product=product)
        except IntegrityError:
            return Response({"error": "Товар уже прикреплен за этим поставщиком"}, status=400)
        return Response(serializer.data, status=201)

    def delete_provider(self, request, *args, **kwargs):
        product = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        provider = serializer.validated_data['provider']
        provider_product = product.providers.filter(provider=provider)
        provider_product.delete()
        return Response(status=204)

    def get_product_income_history(self, request, *args, **kwargs):
        product = Product.objects.filter(pk=self.kwargs['pk']).prefetch_related(
            models.Prefetch(
                'income_items', queryset=IncomeItem.objects.filter(income__status=IncomeStatus.COMPLETED)
            )
        ).first()
        serializer = self.get_serializer(instance=product)
        return Response(serializer.data)


class ProductCompositeListView(ListAPIView):
    queryset = Product.objects.get_available()
    serializer_class = ProductCompositeListSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.select_related('category__industry').prefetch_related(
            models.Prefetch('warehouse_products', WarehouseProduct.objects.filter(count__gt=0))
        )
        qs = qs.with_in_stock().filter(category__is_composite=True)
        return qs


class ProductOptionsView(APIView):

    def get(self, request, *args, **kwargs):
        unit_type_choices = [{'value': choice[0], 'label': choice[1]} for choice in ProductUnitType.choices]
        return Response(unit_type_choices)
