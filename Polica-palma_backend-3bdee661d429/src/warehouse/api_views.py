import io

import pandas as pd

from django.db import models
from django.db.models import Sum, F
from django.http import HttpResponse
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth import get_user_model
from rest_framework import filters
from rest_framework.decorators import action
from rest_framework.generics import ListAPIView, get_object_or_404
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from src.base.api_views import MultiSerializerViewSetMixin, CustomPagination, PermissionPolicyMixin
from src.base.filter_backends import CustomDateRangeFilter
from src.core.enums import ActionPermissionRequestType
from src.core.helpers import create_action_notification
from src.core.models import ActionPermissionRequest, Settings
from src.warehouse.exceptions import NotEnoughProductInWarehouseError
from src.warehouse.filters import WarehouseProductFilter, WarehouseProductWriteOffFilter
from src.warehouse.models import WarehouseProduct, WarehouseProductWriteOff
from src.warehouse.serializers import (
    WarehouseProductSerializer,
    WarehouseProductWriteOffSerializer,
    WarehouseProductWriteOffCreateSerializer, WarehouseProductSummarySerializer
)
from src.warehouse.services import create_warehouse_product_write_off, delete_warehouse_product_write_off

User = get_user_model()


class WarehouseProductViewSet(MultiSerializerViewSetMixin, PermissionPolicyMixin, ModelViewSet):
    queryset = WarehouseProduct.objects.all()
    serializer_class = WarehouseProductSerializer
    serializer_action_classes = {
        'get_summary': WarehouseProductSummarySerializer
    }
    filter_backends = [
        filters.SearchFilter,
        DjangoFilterBackend,
    ]
    pagination_class = CustomPagination

    search_fields = ['product__name', ]
    filterset_class = WarehouseProductFilter

    permission_classes_per_method = {
        "export_excel": [AllowAny],
    }

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.select_related('product') \
            .prefetch_related('product__category', 'product__category__industry') \
            .filter(product__is_deleted=False).by_user_industry(self.request.user)
        qs = qs.filter(count__gt=0)
        return qs

    def get_summary(self, request):
        qs = self.filter_queryset(self.get_queryset())
        total_self_price_sum = qs.aggregate(self_price_sum=Sum(F('self_price') * F('count'), default=0))['self_price_sum']
        return Response(
            WarehouseProductSummarySerializer(instance={'total_self_price_sum': total_self_price_sum}).data
        )

    def export_excel(self, request, *args, **kwargs):
        self.request.user = User.objects.get(pk=kwargs['user_id'])
        qs = self.get_queryset().order_by('product', '-count')
        qs = self.filter_queryset(qs)
        column_names = ['Название', 'Количество', 'Себестоимость', 'Продажная цена', 'Дата']
        columns_data = [
            (
                wh_product.product.name,
                wh_product.count,
                wh_product.self_price,
                wh_product.sale_price,
                timezone.localtime(wh_product.created_at).strftime('%d.%m.%Y %H:%M'),
            ) for wh_product in qs
        ]
        df = pd.DataFrame(columns=column_names, data=columns_data)

        output = io.BytesIO()

        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Sklad')
            ws = writer.sheets['Sklad']
            ws.autofit()

        output.seek(0)

        response = HttpResponse(output,
                                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename=sklad.xlsx'
        return response


class WarehouseProductCompositeListView(ListAPIView):
    queryset = WarehouseProduct.objects.all()
    serializer_class = WarehouseProductSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.select_related('product') \
            .prefetch_related('product__category', 'product__category__industry') \
            .filter(product__is_deleted=False, product__category__is_composite=True)
        return qs


class WarehouseProductWriteOffViewSet(MultiSerializerViewSetMixin, ModelViewSet):
    queryset = WarehouseProductWriteOff.objects.get_available()
    serializer_action_classes = {
        'list': WarehouseProductWriteOffSerializer,
        'create': WarehouseProductWriteOffCreateSerializer,
        'retrieve': WarehouseProductWriteOffSerializer,
    }

    filter_backends = [
        filters.SearchFilter,
        DjangoFilterBackend,
        CustomDateRangeFilter
    ]
    pagination_class = CustomPagination

    search_fields = ['warehouse_product__product__name', ]
    filterset_class = WarehouseProductWriteOffFilter
    filter_date_field = 'created_at',
    date_filter_ignore_actions = [
        'create', 'partial_update', 'update', 'destroy', 'retrieve'
    ]

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.select_related('created_user', 'warehouse_product__product__category__industry')
        qs = qs.filter(
            warehouse_product__product__is_deleted=False,
        ).by_user_industry(self.request.user)
        return qs

    def create(self, request, *args, **kwargs):
        app_settings = Settings.load()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        wh_product: WarehouseProduct = data['warehouse_product']
        try:
            obj = create_warehouse_product_write_off(
                warehouse_product_id=wh_product.pk,
                count=data['count'],
                comment=data.get('comment', None),
                user=request.user
            )
        except NotEnoughProductInWarehouseError as e:
            return Response(data={'error': e}, status=400)
        serializer.instance = obj
        headers = self.get_success_headers(serializer.data)

        if wh_product.product.category.industry.pk not in app_settings.write_off_permission_granted_industries:
            ActionPermissionRequest.objects.create(
                created_user=request.user,
                wh_product_write_off=obj,
                request_type=ActionPermissionRequestType.PRODUCT_WRITE_OFF,
            )
        return Response(serializer.data, status=201, headers=headers)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        delete_warehouse_product_write_off(instance.pk, user=request.user)
        # create_action_notification(
        #     obj_name=str(instance.warehouse_product.product),
        #     action="Отмена списания товара",
        #     user=request.user.get_full_name(),
        #     details=f"Кол-во списания: {instance.count}"
        # )
        return Response(status=204)
