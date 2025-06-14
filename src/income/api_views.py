from django.db import models
from django.db.models import ProtectedError
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from rest_framework import filters
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from src.base.api_views import MultiSerializerViewSetMixin, DestroyFlagsViewSetMixin, CustomPagination
from src.base.filter_backends import CustomDateRangeFilter
from src.factory.models import ProductFactoryItem
from src.income.enums import IncomeStatus
from src.income.exceptions import IncompleteIncomeItemError
from src.income.filters import IncomeFilterSet
from src.income.models import Income, Provider, IncomeItem, ProviderProduct
from src.income.serializers import (
    IncomeListSerializer,
    IncomeDetailSerializer,
    ProviderSerializer,
    IncomeCreateSerializer,
    IncomeItemSerializer,
    IncomeUpdateStatusSerializer,
    IncomeItemCreateSerializer,
    IncomeItemUpdateSerializer, IncomeItemMultipleCreateSerializer, IncomeItemMultipleUpdateSerializer,
    IncomeListSummarySerializer
)
from src.income.services import income_update_total, update_income_status, delete_income, create_or_update_income_item, \
    income_update_total_sale_price
from src.order.models import OrderItemProductOutcome
from src.product.models import Product
from src.product.serializers import ProductListSerializer
from src.warehouse.models import WarehouseProductWriteOff


class IncomeViewSet(MultiSerializerViewSetMixin, ModelViewSet):
    queryset = Income.objects.get_available()
    serializer_action_classes = {
        "list": IncomeListSerializer,
        "retrieve": IncomeDetailSerializer,
        "create": IncomeCreateSerializer,
        "partial_update": IncomeCreateSerializer,
        "get_summary": IncomeListSummarySerializer,
    }
    filter_backends = (
        CustomDateRangeFilter,
        DjangoFilterBackend,
        filters.SearchFilter
    )
    pagination_class = CustomPagination
    filterset_class = IncomeFilterSet
    search_fields = ['id', 'provider__full_name']
    filter_date_field = 'created_at',
    date_filter_ignore_actions = [
        'create', 'partial_update', 'update', 'destroy', 'retrieve'
    ]

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.select_related('created_user', 'provider')

        if self.action in ['retrieve']:
            qs = qs.prefetch_related(
                models.Prefetch(
                    'income_item_set',
                    queryset=IncomeItem.objects.select_related('product__category__industry')
                )
            )
        # qs = qs.by_user_industry(self.request.user)
        return qs

    def perform_create(self, serializer):
        serializer.save(created_user=self.request.user)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        # if not self.request.user.has_active_shift():
        #     return Response(data={'error': 'Необходимо открыть смену'}, status=410)
        delete_income(instance, self.request.user)
        return Response(status=204)

    def get_summary(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        result_data = {
            "total_sum": queryset.aggregate(total_sum=models.Sum('total', default=0))['total_sum'],
            "total_count": len(queryset)
        }
        serializer = self.get_serializer(result_data)
        return Response(serializer.data)



class IncomeItemViewSet(MultiSerializerViewSetMixin, ModelViewSet):
    queryset = IncomeItem.objects.all()
    serializer_class = IncomeItemSerializer
    serializer_action_classes = {
        'list': IncomeItemSerializer,
        'retrieve': IncomeItemSerializer,
        'create': IncomeItemCreateSerializer,
        'update': IncomeItemUpdateSerializer,
        'partial_update': IncomeItemUpdateSerializer,
        'multiple_create': IncomeItemMultipleCreateSerializer,
        'multiple_update': IncomeItemMultipleUpdateSerializer,
    }

    def get_queryset(self):
        income_id = self.kwargs.get('income_id')
        return IncomeItem.objects.filter(income_id=income_id).select_related(
            'product__category__industry',
        )

    def create(self, request, *args, **kwargs):
        income_id = self.kwargs.get('income_id')
        income = get_object_or_404(Income, pk=income_id)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        income_item, created = create_or_update_income_item(income=income, **data)
        if not created:
            return Response(data={'error': 'Товар уже добавлен в закуп'}, status=400)

        income_update_total(income)
        income_update_total_sale_price(income_id)

        serializer.instance = income_item

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=201, headers=headers)

    def perform_update(self, serializer):
        income_id = self.kwargs.get('income_id')
        serializer.save()
        instance = serializer.instance
        instance.total = instance.price * instance.count
        instance.save()
        income_update_total(instance.income)
        income_update_total_sale_price(income_id)

    def perform_destroy(self, instance):
        super().perform_destroy(instance)
        income_update_total(instance.income)
        income_update_total_sale_price(instance.income.pk)

    def multiple_create(self, request, *args, **kwargs):
        income_id = self.kwargs.get('income_id')
        income = get_object_or_404(Income, pk=income_id)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        income_items = serializer.validated_data.get('income_items')
        for item in income_items:
            create_or_update_income_item(income=income, product=item['product'])
            income_update_total(income)
            income_update_total_sale_price(income_id)
        return Response(serializer.data, status=200)

    def multiple_update(self, request, *args, **kwargs):
        income_id = self.kwargs.get('income_id')
        income = get_object_or_404(Income, pk=income_id)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        income_items = serializer.validated_data.get('income_items')

        income_items = list(filter(lambda x: not None in x.values(), income_items))

        # for item in income_items:
        #     if 0 in item.values():
        #         return Response(data={'error': 'Существуют незаполненные элементы прихода'}, status=400)

        for item in income_items:
            instance = get_object_or_404(IncomeItem, pk=item['id'])
            instance.count = item.get('count', instance.count)
            instance.price = item.get('price', instance.price)
            instance.sale_price = item.get('sale_price', instance.sale_price)
            instance.total = instance.price * instance.count
            instance.total_sale_price = instance.sale_price * instance.count
            instance.save()
            income_update_total(instance.income)
            income_update_total_sale_price(income_id)
        return Response(serializer.data, status=200)


class IncomeUpdateStatusView(APIView):

    @swagger_auto_schema(
        request_body=IncomeUpdateStatusSerializer(),
        responses={200: IncomeUpdateStatusSerializer()}
    )
    def post(self, request, *args, **kwargs):
        income_id = self.kwargs.get('pk')
        income = get_object_or_404(Income, pk=income_id)

        serializer = IncomeUpdateStatusSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        status = validated_data.get('status')
        try:
            update_income_status(income, status, request.user)
        except IncompleteIncomeItemError as e:
            return Response(data={'error': str(e)}, status=400)
        return Response(serializer.data)


class ProviderViewSet(MultiSerializerViewSetMixin, DestroyFlagsViewSetMixin, ModelViewSet):
    queryset = Provider.objects.get_available()
    serializer_class = ProviderSerializer
    serializer_action_classes = {
        'get_products': ProductListSerializer
    }
    filter_backends = [
        filters.SearchFilter
    ]
    search_fields = ['full_name', 'phone_number']

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.by_user_industry(self.request.user)
        return qs

    def perform_create(self, serializer):
        serializer.save(created_user=self.request.user)

    def get_products(self, request, *args, **kwargs):
        instance = self.get_object()
        provider_products = ProviderProduct.objects.filter(provider=instance)
        products = Product.objects.get_available().with_in_stock().filter(providers__in=provider_products)
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)


class IncomeStatusOptionsView(APIView):
    def get(self, request):
        status_choices = [{'value': choice[0], 'label': choice[1]} for choice in IncomeStatus.choices]
        return Response(status_choices, status=200)
