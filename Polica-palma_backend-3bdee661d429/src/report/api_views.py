from collections import defaultdict
from decimal import Decimal
from itertools import chain

from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import QuerySet, Sum, F
from django.db.models.functions import Coalesce
from django.http import FileResponse
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import filters
from rest_framework.generics import ListAPIView, RetrieveAPIView, get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet, ViewSet

from src.base.api_views import CustomPagination
from src.core.helpers import try_parsing_date
from src.factory.enums import ProductFactoryStatus, ProductFactorySalesType
from src.factory.models import ProductFactory, ProductFactoryItem, ProductFactoryItemReturn
from src.income.enums import IncomeStatus
from src.income.models import IncomeItem
from src.order.enums import OrderStatus
from src.order.models import Order, OrderItem, OrderItemProductFactory, Client, OrderItemProductReturn
from src.payment.enums import PaymentType
from src.payment.models import Payment
from src.product.models import Product
from src.report.filters import (
    OrderFilter,
    OrderItemReturnFilter,
    OrderItemProductFactoryReturnFilter,
    WriteOffReportProductFilter,
    WriteOffReportProductFactoryFilter,
    ProductFactoriesReportProductFactoryFilter, OrderItemFilter, ProductFilter, OrderItemProductFactoryFilter,
    WorkerIncomeFilter, WorkersFilter
)
from src.report.helpers import MaterialReportExcelExport, OrderReportExcelExport, SalesmanReportExcelExport, \
    FloristReportExcelExport, WriteOffReportExcelExport, ClientsReportExcelExport, ProductReturnReportExcelExport, \
    ProductFactoryReportExcelExport, OrderItemsReportExcelExport, OtherWorkersReportExcelExport, \
    WorkersReportExcelExport
from src.report.serializers import (
    OrderReportSerializer,
    MaterialReportSerializer,
    MaterialReportDetailSerializer,
    SalesmenReportSummarySerializer,
    FloristReportSummarySerializer,
    ClientsReportSerializer,
    ProductReturnsReportSerializer,
    WriteOffsReportProductListSerializer,
    WriteOffsReportProductFactoryListSerializer,
    WriteOffsReportSummarySerializer,
    ProductFactoriesReportProductListSerializer,
    ProductFactoriesReportSummarySerializer,
    ProductReturnsReportProductReturnListSerializer,
    ProductReturnsReportProductFactoryReturnListSerializer,
    MaterialReportOrderListSerializer,
    MaterialReportIncomeListSerializer,
    MaterialReportProductFactoryListSerializer,
    MaterialReportWriteOffListSerializer,
    MaterialReportOrderItemReturnListSerializer,
    MaterialReportFactoryItemReturnListSerializer, WorkerIncomeSerializer, SalesmenReportWorkerListSerializer,
    WorkerPaymentSerializer, SalesmenReportOrderSerializer, FloristsReportFloristListSerializer,
    FloristReportProductFactorySerializer, WriteOffsReportProductWriteOffSerializer, ClientsReportOrderSerializer,
    ClientsReportClientListSerializer, OrderItemsReportSerializer, OrderItemsReportItemListSerializer,
    OrderItemsReportFactoryItemListSerializer, OtherWorkersReportListSerializer, OtherWorkersReportSummarySerializer,
    SalesmenReportDetailSerializer, FloristReportDetailSerializer, WorkersReportSummarySerializer,
    WorkersReportWorkerListSerializer, WorkersReportDetailSerializer, OverallReportSerializer
)
from src.report.services import (
    get_total_product_outcome,
    get_total_product_income,
    get_client_debt,
    get_client_orders_count,
    get_client_orders_sum,
    get_write_offs_report_product_factories,
    get_write_offs_report_products,
    get_factories_report_product_factories,
    get_returns_report_product_returns,
    get_returns_report_factories_returns,
    get_material_report_factory_item_returns,
    get_material_report_order_item_returns,
    get_material_report_write_offs,
    get_material_report_factories,
    get_material_report_incomes,
    get_material_report_orders, get_salesman_orders, get_worker_incomes, get_worker_payments, get_salesman_list,
    get_florist_list, get_florist_product_factories, get_product_write_offs, get_clients_orders,
    get_client_orders_discount_sum, get_order_items_report_products, order_items_report_factories,
    get_other_worker_list, get_worker_list, get_total_product_income_sub, get_total_product_outcome_sub
)
from src.user.enums import WorkerIncomeType, UserType, WorkerIncomeReason
from src.user.models import WorkerIncomes
from src.warehouse.models import WarehouseProductWriteOff

User = get_user_model()


class ReportCommonFiltersMixin:
    def get_start_end_dates(self):
        start_date = self.request.query_params.get('start_date', None)
        end_date = self.request.query_params.get('end_date', None)

        if not start_date or start_date == "":
            start_date = timezone.now().replace(day=1, hour=0, minute=0, second=0,
                                                tzinfo=timezone.get_current_timezone())
        if not end_date or end_date == "":
            end_date = timezone.now()

        if type(start_date) is str and len(start_date) > 0:
            start_date = timezone.make_aware(try_parsing_date(start_date))
        if type(end_date) is str and len(end_date) > 0:
            end_date = timezone.make_aware(try_parsing_date(end_date).replace(
                hour=23, minute=59, second=59
            ))

        return start_date, end_date

    def get_industry(self):
        return self.request.query_params.get('industry')

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('start_date', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description="Start date in DD.MM.YYYY format"),
            openapi.Parameter('end_date', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description="End date in DD.MM.YYYY format"),
            openapi.Parameter('industry', in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER),
        ]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class IndustryFilterMixin:
    def get_industry(self):
        return self.request.query_params.get('industry')

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('industry', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING),
        ]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class DateRangeFilterMixin:
    def get_start_end_dates(self):
        start_date = self.request.query_params.get('start_date', None)
        end_date = self.request.query_params.get('end_date', None)

        if not start_date or start_date == "":
            start_date = timezone.now().replace(day=1, hour=0, minute=0, second=0,
                                                tzinfo=timezone.get_current_timezone())
        if not end_date or end_date == "":
            end_date = timezone.now()

        if type(start_date) is str and len(start_date) > 0:
            start_date = timezone.make_aware(try_parsing_date(start_date))
        if type(end_date) is str and len(end_date) > 0:
            end_date = timezone.make_aware(try_parsing_date(end_date)).replace(hour=23, minute=59, second=59)

        return start_date, end_date

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('start_date', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description="Start date in DD.MM.YYYY format"),
            openapi.Parameter('end_date', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description="End date in DD.MM.YYYY format"),
        ]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class DateTimeRangeFilterMixin:
    def get_start_end_dates(self):
        start_date = self.request.query_params.get('start_date', None)
        end_date = self.request.query_params.get('end_date', None)

        if not start_date or start_date == "":
            start_date = timezone.now().replace(day=1, hour=0, minute=0, second=0,
                                                tzinfo=timezone.get_current_timezone())
        if not end_date or end_date == "":
            end_date = timezone.now()

        if type(start_date) is str and len(start_date) > 0:
            start_date = timezone.make_aware(try_parsing_date(start_date))
        if type(end_date) is str and len(end_date) > 0:
            end_date = timezone.make_aware(try_parsing_date(end_date))

        return start_date, end_date

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('start_date', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description="Start date in DD.MM.YYYY HH:mm format"),
            openapi.Parameter('end_date', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description="End date in DD.MM.YYYY HH:mm format"),
        ]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class ExportDisablePermissionMixin:
    def get_permissions(self):
        if self.action == 'get_excel_report':
            return []  # Disable permissions for this action
        return super().get_permissions()


# =================== OrderReport =================== #
class OrderReportView(DateTimeRangeFilterMixin, ExportDisablePermissionMixin, ModelViewSet):
    queryset = Order.objects.get_available()
    serializer_class = OrderReportSerializer
    pagination_class = CustomPagination
    filter_backends = (
        DjangoFilterBackend,
        filters.SearchFilter
    )
    filterset_class = OrderFilter
    search_fields = [
        'id',
        'created_user__first_name',
        'created_user__last_name',
        'salesman__first_name',
        'salesman__last_name',
        'created_user__industry__name',
        'salesman__industry__name'
    ]

    def get_queryset(self):
        start_date, end_date = self.get_start_end_dates()
        qs = super().get_queryset()
        qs = qs.select_related('client', 'completed_user', 'created_user__industry', 'salesman__industry')
        qs = qs.prefetch_related(
            models.Prefetch(
                'order_items',
                queryset=OrderItem.objects.prefetch_related(
                    'product', 'product__category', 'product__category__industry',
                )
            ),
            models.Prefetch(
                'order_item_product_factory_set',
                queryset=OrderItemProductFactory.objects.select_related('product_factory')
            ),
        )
        qs = qs.filter(
            created_at__gte=start_date,
            created_at__lte=end_date
        )
        # if industries:
        #     qs = qs.by_industries(industries)
        if self.request.user.type == UserType.MANAGER:
            qs = qs.by_user_industry(self.request.user)
        qs = qs.filter(~models.Q(status=OrderStatus.CANCELLED))
        qs = qs.with_amount_paid().with_total_discount().with_total_charge().with_total_self_price() \
            .with_total_profit().with_total_debt().with_products_discount()
        qs = qs.order_by('-created_at')
        return qs

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('start_date', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description="Start date in DD.MM.YYYY format"),
            openapi.Parameter('end_date', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description="End date in DD.MM.YYYY format"),
            openapi.Parameter('industry', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING),
            openapi.Parameter('salesman', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING),

        ]
    )
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        aggregated_data = self.get_aggregated_data(queryset)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.serializer_class.create_(orders=page, **aggregated_data)
            return self.get_paginated_response(serializer.data)

        serializer = self.serializer_class.create_(orders=queryset, **aggregated_data)
        return Response(serializer.data)

    def get_aggregated_data(self, orders):
        aggregated_data = orders.aggregate(
            total_sale_amount=models.Sum(models.F('total') + models.F('products_discount'), default=0),
            total_sale_with_discount_amount=models.Sum('total_with_discount', default=0),
            total_discount_amount=models.Sum('total_discount', default=0),
            total_charge_amount=models.Sum('total_charge', default=0),
            total_self_price_amount=models.Sum('total_self_price', default=0),
            total_profit_amount=models.Sum('total_profit', default=0),
            total_debt_amount=models.Sum('debt', default=0),
            total_paid_amount=models.Sum('amount_paid', default=0)
        )
        return {
            'total_sale_amount': aggregated_data['total_sale_amount'],
            'total_sale_with_discount_amount': aggregated_data['total_sale_with_discount_amount'],
            'total_discount_amount': aggregated_data['total_discount_amount'],
            'total_charge_amount': aggregated_data['total_charge_amount'],
            'total_self_price_amount': aggregated_data['total_self_price_amount'],
            'total_profit_amount': aggregated_data['total_profit_amount'],
            'total_debt_amount': aggregated_data['total_debt_amount'],
            'total_paid_amount': aggregated_data['total_paid_amount'],
        }

    def get_excel_report(self, request, *args, **kwargs):
        start_date, end_date = self.get_start_end_dates()
        self.request.user = User.objects.get(pk=kwargs['user_id'])
        data = self.filter_queryset(self.get_queryset())
        aggregated_data = self.get_aggregated_data(data)
        byte_buffer = OrderReportExcelExport(data, aggregated_data, start_date, end_date).get_excel_file()
        return FileResponse(byte_buffer, filename='Prodazhi_otchet.xlsx', as_attachment=True)


# =================== MaterialReport =================== #
class MaterialReportView(ReportCommonFiltersMixin, ExportDisablePermissionMixin, ModelViewSet):
    queryset = Product.objects.get_available()
    serializer_class = MaterialReportSerializer
    pagination_class = CustomPagination
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
    ]
    filterset_class = ProductFilter
    search_fields = [
        'name',
        'category__industry__name'
    ]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('start_date', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description="Start date in DD.MM.YYYY format"),
            openapi.Parameter('end_date', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description="End date in DD.MM.YYYY format"),
            openapi.Parameter('industry', in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER),
            openapi.Parameter('category', in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER),
            openapi.Parameter('client', in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER),
            openapi.Parameter('created_user', in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER),
            openapi.Parameter('salesman', in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER),
        ]
    )
    def get(self, request):
        return super().get(request)

    def get_order_filters(self):
        clients = self.request.query_params.getlist('client')
        salesmen = self.request.query_params.getlist('salesman')
        created_users = self.request.query_params.getlist('created_user')
        order_filters = {
            'order__client__in': clients,
            'order__salesman__in': salesmen,
            'order__created_user__in': created_users,
        }
        order_filters = {k: v for k, v in order_filters.items() if v is not None}
        return order_filters

    def annotate_total_outcome(self, products, start_date, end_date, field_name):
        order_filters = self.get_order_filters()

        order_items = OrderItem.objects.filter(
            models.Q(product__in=products)
            & ~models.Q(order__status=OrderStatus.CANCELLED)
            & models.Q(order__created_at__gte=start_date)
            & models.Q(order__created_at__lte=end_date)
        ).values('product_id', 'count')
        factory_items = ProductFactoryItem.objects.filter(
            models.Q(warehouse_product__product__in=products)
            & models.Q(factory__is_deleted=False)
            & models.Q(factory__created_at__gte=start_date)
            & models.Q(factory__created_at__lte=end_date)
        ).annotate(product_id=F('warehouse_product__product_id')).values('product_id', 'count')
        warehouse_products = WarehouseProductWriteOff.objects.filter(
            warehouse_product__product__in=products,
            is_deleted=False,
            created_at__gte=start_date,
            created_at__lte=end_date
        ).annotate(product_id=F('warehouse_product__product_id')).values('product_id', 'count')

        combined_queryset = chain(order_items, factory_items, warehouse_products)

        product_counts = defaultdict(int)
        for item in combined_queryset:
            product_counts[item['product_id']] += item['count']

        for product in products:
            setattr(product, field_name, product_counts[product.pk])

    def annotate_total_income(self, products, start_date, end_date, field_name):
        income_items = IncomeItem.objects.filter(
            product__in=products,
            income__status=IncomeStatus.COMPLETED,
            income__is_deleted=False,
            income__created_at__gte=start_date,
            income__created_at__lte=end_date,
        ).values('product_id', 'count')
        order_product_returns = OrderItemProductReturn.objects.filter(
            order_item__product__in=products,
            is_deleted=False,
            created_at__gte=start_date,
            created_at__lte=end_date
        ).annotate(product_id=F('order_item__product_id')).values('product_id', 'count')
        factory_returns = ProductFactoryItemReturn.objects.filter(
            factory_item__warehouse_product__product__in=products,
            is_deleted=False,
            created_at__gte=start_date,
            created_at__lte=end_date,
        ).annotate(product_id=F('factory_item__warehouse_product__product_id')).values('product_id', 'count')

        combined_queryset = chain(income_items, order_product_returns, factory_returns)

        product_counts = defaultdict(int)
        for item in combined_queryset:
            product_counts[item['product_id']] += item['count']

        for product in products:
            setattr(product, field_name, product_counts[product.pk])

    def annotate_before_and_after_count(self, products):
        for product in products:
            total_income = product.total_income_in_range + product.total_income_after_range
            total_outcome = product.total_outcome_in_range + product.total_outcome_after_range
            product.before_count = product.in_stock - total_income + total_outcome
            product.after_count = product.in_stock - (product.total_income_after_range
                                                      - product.total_outcome_after_range)

    def get_queryset(self):
        qs = super().get_queryset()
        start_date, end_date = self.get_start_end_dates()

        qs = qs.select_related('category__industry').defer('image', 'unit_type', 'price')
        qs = qs.by_user_industry(self.request.user).with_in_stock()

        if self.request.user.type == UserType.MANAGER:
            qs = qs.filter(category__industry=self.request.user.industry)

        return qs

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('start_date', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description="Start date in DD.MM.YYYY format"),
            openapi.Parameter('end_date', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description="End date in DD.MM.YYYY format"),
            openapi.Parameter('industry', in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER),
            openapi.Parameter('category', in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER),
            openapi.Parameter('client', in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER),
            openapi.Parameter('created_user', in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER),
            openapi.Parameter('salesman', in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER),
        ]
    )
    def list(self, request, *args, **kwargs):
        start_date, end_date = self.get_start_end_dates()
        queryset = self.filter_queryset(self.get_queryset())
        self.annotate_total_outcome(queryset, start_date, end_date, 'total_outcome_in_range')
        self.annotate_total_outcome(queryset, end_date, timezone.now(), 'total_outcome_after_range')
        self.annotate_total_income(queryset, start_date, end_date, 'total_income_in_range')
        self.annotate_total_income(queryset, end_date, timezone.now(), 'total_income_after_range')
        self.annotate_before_and_after_count(queryset)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.serializer_class.create_(products=page)
            return self.get_paginated_response(serializer.data)

        serializer = self.serializer_class.create_(products=queryset)
        return Response(serializer.data)

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('start_date', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description="Start date in DD.MM.YYYY format"),
            openapi.Parameter('end_date', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description="End date in DD.MM.YYYY format"),
            openapi.Parameter('industry', in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER),
            openapi.Parameter('category', in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER),
            openapi.Parameter('client', in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER),
            openapi.Parameter('created_user', in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER),
            openapi.Parameter('salesman', in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER),
        ]
    )
    def get_excel_report(self, request, *args, **kwargs):
        start_date, end_date = self.get_start_end_dates()
        self.request.user = User.objects.get(pk=kwargs['user_id'])
        queryset = self.filter_queryset(self.get_queryset())
        self.annotate_total_outcome(queryset, start_date, end_date, 'total_outcome_in_range')
        self.annotate_total_outcome(queryset, end_date, timezone.now(), 'total_outcome_after_range')
        self.annotate_total_income(queryset, start_date, end_date, 'total_income_in_range')
        self.annotate_total_income(queryset, end_date, timezone.now(), 'total_income_after_range')
        self.annotate_before_and_after_count(queryset)
        # data = ProductFilter(data=request.query_params, queryset=self.get_queryset()).qs
        byte_buffer = MaterialReportExcelExport(queryset, start_date, end_date).get_excel_file()
        return FileResponse(byte_buffer, filename='Matrialniy_otchet.xlsx', as_attachment=True)


class MaterialReportTestView(ReportCommonFiltersMixin, ExportDisablePermissionMixin, ModelViewSet):
    queryset = Product.objects.get_available()
    serializer_class = MaterialReportSerializer
    pagination_class = CustomPagination
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
    ]
    filterset_class = ProductFilter
    search_fields = [
        'name',
        'category__industry__name'
    ]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('start_date', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description="Start date in DD.MM.YYYY format"),
            openapi.Parameter('end_date', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description="End date in DD.MM.YYYY format"),
            openapi.Parameter('industry', in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER),
            openapi.Parameter('category', in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER),
        ]
    )
    def get(self, request):
        return super().get(request)

    def get_queryset(self):
        qs = super().get_queryset()
        start_date, end_date = self.get_start_end_dates()

        qs = qs.select_related('category__industry').prefetch_related('warehouse_products') \
            .defer('image', 'unit_type', 'price')
        qs = qs.by_user_industry(self.request.user).annotate(
            in_stock=models.Sum('warehouse_products__count', default=0, distinct=True)
        )

        if self.request.user.type == UserType.MANAGER:
            qs = qs.filter(category__industry=self.request.user.industry)

        qs = qs.annotate(
            total_income_in_range=get_total_product_income_sub(start_date, end_date),
            total_outcome_in_range=get_total_product_outcome_sub(start_date, end_date),
            total_income_after_range=get_total_product_income_sub(end_date, timezone.now()),
            total_outcome_after_range=get_total_product_outcome_sub(end_date, timezone.now()),
            # before_count=Coalesce(
            #     models.F('in_stock') - (models.F('total_income_in_range') + models.F('total_income_after_range'))
            #     + (models.F('total_outcome_in_range') + models.F('total_outcome_after_range')),
            #     models.Value(0), output_field=models.DecimalField()
            # ),
            # after_count=Coalesce(
            #     models.F('in_stock') - (models.F('total_income_after_range') - models.F('total_outcome_after_range')),
            #     models.Value(0), output_field=models.DecimalField()
            # ),
        )

        return qs

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('start_date', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description="Start date in DD.MM.YYYY format"),
            openapi.Parameter('end_date', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description="End date in DD.MM.YYYY format"),
            openapi.Parameter('industry', in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER),
            openapi.Parameter('category', in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER),
        ]
    )
    def list(self, request, *args, **kwargs):
        # queryset = self.get_queryset()
        queryset = self.filter_queryset(self.get_queryset())
        # queryset = ProductFilter(data=request.query_params, queryset=queryset).qs
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.serializer_class.create_(products=page)
            return self.get_paginated_response(serializer.data)

        serializer = self.serializer_class.create_(products=queryset)
        return Response(serializer.data)

    def annotate_before_and_after_count(self, products):
        for product in products:
            total_income = product.total_income_in_range + product.total_income_after_range
            total_outcome = product.total_outcome_in_range + product.total_outcome_after_range
            product.before_count = product.in_stock - total_income + total_outcome
            product.after_count = product.in_stock - (product.total_income_after_range
                                                      - product.total_outcome_after_range)

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('start_date', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description="Start date in DD.MM.YYYY format"),
            openapi.Parameter('end_date', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description="End date in DD.MM.YYYY format"),
            openapi.Parameter('industry', in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER),
            openapi.Parameter('category', in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER),
        ]
    )
    def get_excel_report(self, request, *args, **kwargs):
        start_date, end_date = self.get_start_end_dates()
        self.request.user = User.objects.get(pk=kwargs['user_id'])
        data = ProductFilter(data=request.query_params, queryset=self.get_queryset()).qs
        self.annotate_before_and_after_count(data)
        byte_buffer = MaterialReportExcelExport(data, start_date, end_date).get_excel_file()
        return FileResponse(byte_buffer, filename='Matrialniy_otchet.xlsx', as_attachment=True)


class MaterialReportOrderListView(DateRangeFilterMixin, ListAPIView):
    serializer_class = MaterialReportOrderListSerializer
    pagination_class = CustomPagination
    filter_backends = [
        filters.SearchFilter,
        DjangoFilterBackend
    ]
    search_fields = [
        'id',
        'client__full_name'
    ]
    filterset_class = OrderFilter

    def get_queryset(self):
        start_date, end_date = self.get_start_end_dates()
        product_id = self.kwargs.get('pk')
        product = get_object_or_404(Product, pk=product_id)
        return get_material_report_orders(product, start_date, end_date)


class MaterialReportIncomesListView(DateRangeFilterMixin, ListAPIView):
    serializer_class = MaterialReportIncomeListSerializer
    pagination_class = CustomPagination
    filter_backends = [
        filters.SearchFilter
    ]
    search_fields = [
        'provider__full_name'
    ]

    def get_queryset(self):
        start_date, end_date = self.get_start_end_dates()
        product_id = self.kwargs.get('pk')
        product = get_object_or_404(Product, pk=product_id)
        return get_material_report_incomes(product, start_date, end_date)


class MaterialReportProductFactoryListView(DateRangeFilterMixin, ListAPIView):
    serializer_class = MaterialReportProductFactoryListSerializer
    pagination_class = CustomPagination
    filter_backends = [
        filters.SearchFilter
    ]
    search_fields = [
        'name'
    ]

    def get_queryset(self):
        start_date, end_date = self.get_start_end_dates()
        product_id = self.kwargs.get('pk')
        product = get_object_or_404(Product, pk=product_id)
        return get_material_report_factories(product, start_date, end_date)


class MaterialReportWriteOffListView(DateRangeFilterMixin, ListAPIView):
    serializer_class = MaterialReportWriteOffListSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        start_date, end_date = self.get_start_end_dates()
        product_id = self.kwargs.get('pk')
        product = get_object_or_404(Product, pk=product_id)
        return get_material_report_write_offs(product, start_date, end_date)


class MaterialReportOrderItemReturnListView(DateRangeFilterMixin, ListAPIView):
    serializer_class = MaterialReportOrderItemReturnListSerializer
    pagination_class = CustomPagination
    filter_backends = [
        filters.SearchFilter
    ]
    search_fields = [
        'order_item__order__id'
    ]

    def get_queryset(self):
        start_date, end_date = self.get_start_end_dates()
        product_id = self.kwargs.get('pk')
        product = get_object_or_404(Product, pk=product_id)
        return get_material_report_order_item_returns(product, start_date, end_date)


class MaterialReportFactoryItemReturnListView(DateRangeFilterMixin, ListAPIView):
    serializer_class = MaterialReportFactoryItemReturnListSerializer
    pagination_class = CustomPagination
    filter_backends = [
        filters.SearchFilter
    ]
    search_fields = [
        'factory_item__factory__name'
    ]

    def get_queryset(self):
        start_date, end_date = self.get_start_end_dates()
        product_id = self.kwargs.get('pk')
        product = get_object_or_404(Product, pk=product_id)
        return get_material_report_factory_item_returns(product, start_date, end_date)


class MaterialReportDetailView(DateRangeFilterMixin, RetrieveAPIView):
    queryset = Product.objects.all()

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('start_date', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description="Start date in DD.MM.YYYY format"),
            openapi.Parameter('end_date', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description="End date in DD.MM.YYYY format"),
            openapi.Parameter('industry', in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER),
            openapi.Parameter('client', in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER),
            openapi.Parameter('created_user', in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER),
            openapi.Parameter('salesman', in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER),
        ]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_order_filters(self):
        clients = self.request.query_params.getlist('client')
        salesmen = self.request.query_params.getlist('salesman')
        created_users = self.request.query_params.getlist('created_user')
        order_filters = {
            'client__in': clients,
            'salesman__in': salesmen,
            'created_user__in': created_users,
        }
        order_filters = {k: v for k, v in order_filters.items() if not len(v) == 0}
        return order_filters

    def annotate_total_outcome(self, product, start_date, end_date, field_name):
        order_items = OrderItem.objects.filter(
            models.Q(product=product)
            & ~models.Q(order__status=OrderStatus.CANCELLED)
            & models.Q(order__created_at__gte=start_date)
            & models.Q(order__created_at__lte=end_date)
        ).values('product_id', 'count')
        factory_items = ProductFactoryItem.objects.filter(
            models.Q(warehouse_product__product=product)
            & models.Q(factory__is_deleted=False)
            & models.Q(factory__created_at__gte=start_date)
            & models.Q(factory__created_at__lte=end_date)
        ).annotate(product_id=F('warehouse_product__product_id')).values('product_id', 'count')
        warehouse_products = WarehouseProductWriteOff.objects.filter(
            warehouse_product__product=product,
            is_deleted=False,
            created_at__gte=start_date,
            created_at__lte=end_date
        ).annotate(product_id=F('warehouse_product__product_id')).values('product_id', 'count')

        combined_queryset = chain(order_items, factory_items, warehouse_products)

        product_counts = defaultdict(int)
        for item in combined_queryset:
            product_counts[item['product_id']] += item['count']

        setattr(product, field_name, product_counts[product.pk])

    def annotate_total_income(self, product, start_date, end_date, field_name):
        income_items = IncomeItem.objects.filter(
            product=product,
            income__status=IncomeStatus.COMPLETED,
            income__is_deleted=False,
            income__created_at__gte=start_date,
            income__created_at__lte=end_date,
        ).values('product_id', 'count')
        order_product_returns = OrderItemProductReturn.objects.filter(
            order_item__product=product,
            is_deleted=False,
            created_at__gte=start_date,
            created_at__lte=end_date
        ).annotate(product_id=F('order_item__product_id')).values('product_id', 'count')
        factory_returns = ProductFactoryItemReturn.objects.filter(
            factory_item__warehouse_product__product=product,
            is_deleted=False,
            created_at__gte=start_date,
            created_at__lte=end_date,
        ).annotate(product_id=F('factory_item__warehouse_product__product_id')).values('product_id', 'count')

        combined_queryset = chain(income_items, order_product_returns, factory_returns)

        product_counts = defaultdict(int)
        for item in combined_queryset:
            product_counts[item['product_id']] += item['count']

        setattr(product, field_name, product_counts[product.pk])

    def annotate_before_and_after_count(self, product):
        total_income = product.total_income_in_range + product.total_income_after_range
        total_outcome = product.total_outcome_in_range + product.total_outcome_after_range
        product.before_count = product.in_stock - total_income + total_outcome
        product.after_count = product.in_stock - (product.total_income_after_range
                                                  - product.total_outcome_after_range)

    def get_queryset(self):
        qs = super().get_queryset()

        qs = qs.filter(pk=self.kwargs['pk']).prefetch_related('warehouse_products').annotate(
            in_stock=models.Sum('warehouse_products__count', default=0, distinct=True)
        )

        return qs

    def retrieve(self, request, *args, **kwargs):
        start_date, end_date = self.get_start_end_dates()
        industry = request.query_params.get('industry', None)
        order_filters = self.get_order_filters()
        product = self.get_object()
        orders = get_material_report_orders(product, start_date, end_date, industry).filter(**order_filters)
        # incomes = get_material_report_incomes(product, start_date, end_date)
        # factory_products = get_material_report_factories(product, start_date, end_date)
        # write_offs = get_material_report_write_offs(product, start_date, end_date)
        # order_returns = get_material_report_order_item_returns(product, start_date, end_date)
        # factory_returns = get_material_report_factory_item_returns(product, start_date, end_date)
        self.annotate_total_outcome(product, start_date, end_date, 'total_outcome_in_range')
        self.annotate_total_outcome(product, end_date, timezone.now(), 'total_outcome_after_range')
        self.annotate_total_income(product, start_date, end_date, 'total_income_in_range')
        self.annotate_total_income(product, end_date, timezone.now(), 'total_income_after_range')
        self.annotate_before_and_after_count(product)

        orders_aggregates = orders.aggregate(
            product_sales_sum=Sum('total_product_sum', default=0),
            self_price_sum=Sum('total_product_self_price', default=0),
            total_sales_count=Sum('product_count', default=0),
        )
        data = dict(
            name=product.name,
            total_income_in_range=product.total_income_in_range,
            total_outcome_in_range=product.total_outcome_in_range,
            # total_income_after_range=product.total_income_after_range,
            # total_outcome_after_range=product.total_outcome_after_range,
            # total_income_before_range=product.total_income_before_range,
            # total_outcome_before_range=product.total_outcome_before_range,
            before_count=product.before_count,
            after_count=product.after_count,
            # product_in_orders_count=self.get_sum_count(orders, 'product_count'),
            # product_in_incomes_count=self.get_sum_count(incomes, 'product_count'),
            # product_in_factories_count=self.get_sum_count(factory_products, 'product_count'),
            # product_write_offs_count=self.get_sum_count(write_offs, 'count'),
            # product_order_returns_count=self.get_sum_count(order_returns, 'count'),
            # product_factory_returns_count=self.get_sum_count(factory_returns, 'count'),
            current_count=product.in_stock,
            total_sales_in_range=orders_aggregates['product_sales_sum'],
            total_self_price_in_range=orders_aggregates['self_price_sum'],
            total_sales_count=orders_aggregates['total_sales_count'],
        )
        serializer = MaterialReportDetailSerializer.create_(
            **data
        )
        return Response(serializer.data)

    def get_sum_count(self, queryset, count_field):
        return queryset.aggregate(count_sum=models.Sum(count_field, default=0))['count_sum']


# =================== SalesmenReport =================== #

class SalesmenReportSalesmenListView(DateTimeRangeFilterMixin, IndustryFilterMixin, ListAPIView):
    serializer_class = SalesmenReportWorkerListSerializer
    pagination_class = CustomPagination
    filter_backends = [
        filters.SearchFilter
    ]
    search_fields = [
        'first_name',
        'last_name',
        'industry__name'
    ]

    def get_queryset(self):
        start_date, end_date = self.get_start_end_dates()
        industry = self.request.query_params.getlist('industry')

        return get_salesman_list(self.request, industry, start_date, end_date)


class SalesmenReportSummaryView(DateTimeRangeFilterMixin, IndustryFilterMixin, ExportDisablePermissionMixin, ViewSet):

    def get_queryset(self):
        start_date, end_date = self.get_start_end_dates()
        industry = self.request.query_params.getlist('industry')
        return get_salesman_list(self.request, industry, start_date, end_date)

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('start_date', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description="Start date in DD.MM.YYYY format"),
            openapi.Parameter('end_date', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description="End date in DD.MM.YYYY format"),
            openapi.Parameter('industry', in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER),
        ]
    )
    def list(self, request, *args, **kwargs):
        salesman_list = self.get_queryset()
        aggregated_data = self.get_aggregated_data(salesman_list)
        serializer = SalesmenReportSummarySerializer(instance={**aggregated_data})
        return Response(serializer.data)

    def get_aggregated_data(self, salesmen):
        aggregations = salesmen.aggregate(
            total_orders_count=models.Sum('orders_count'),
            total_orders_sum=models.Sum('order_total_sum'),
            total_income_sum=models.Sum('income_sum'),
            total_payment_sum=models.Sum('payment_sum')
        )

        total_orders_count = aggregations['total_orders_count']
        total_orders_sum = aggregations['total_orders_sum']
        total_income_sum = aggregations['total_income_sum']
        total_payments_sum = aggregations['total_payment_sum']

        return {
            'total_orders_count': total_orders_count,
            'total_orders_sum': total_orders_sum,
            'total_income_sum': total_income_sum,
            'total_payments_sum': total_payments_sum,
        }

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('start_date', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description="Start date in DD.MM.YYYY format"),
            openapi.Parameter('end_date', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description="End date in DD.MM.YYYY format"),
            openapi.Parameter('industry', in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER),
        ]
    )
    def get_excel_report(self, request, *args, **kwargs):
        start_date, end_date = self.get_start_end_dates()
        self.request.user = User.objects.get(pk=kwargs['user_id'])
        salesman_list = self.get_queryset()
        aggregated_data = self.get_aggregated_data(salesman_list)
        byte_buffer = SalesmanReportExcelExport(salesman_list, aggregated_data, start_date, end_date).get_excel_file()
        return FileResponse(byte_buffer, filename='Prodavci_otchet.xlsx', as_attachment=True)


class WorkerIncomeListView(DateTimeRangeFilterMixin, ListAPIView):
    serializer_class = WorkerIncomeSerializer
    pagination_class = CustomPagination
    filter_backends = [
        filters.SearchFilter,
        DjangoFilterBackend,
    ]
    search_fields = [
        'order__id',
        'reason',
        'salary_info',
    ]
    filterset_class = WorkerIncomeFilter

    def get_queryset(self):
        worker_id = self.kwargs.get('pk')
        worker = get_object_or_404(User, pk=worker_id)
        start_date, end_date = self.get_start_end_dates()
        return get_worker_incomes(worker, start_date, end_date)


class WorkerPaymentListView(DateTimeRangeFilterMixin, ListAPIView):
    serializer_class = WorkerPaymentSerializer
    pagination_class = CustomPagination
    filter_backends = [
        filters.SearchFilter
    ]
    search_fields = [
        'order__id',
    ]

    def get_queryset(self):
        worker_id = self.kwargs.get('pk')
        worker = get_object_or_404(User, pk=worker_id)
        start_date, end_date = self.get_start_end_dates()
        return get_worker_payments(worker, start_date, end_date)


class SalesmenReportOrderListView(DateTimeRangeFilterMixin, ListAPIView):
    serializer_class = SalesmenReportOrderSerializer
    pagination_class = CustomPagination
    filter_backends = [
        filters.SearchFilter
    ]
    search_fields = [
        'id',
    ]

    def get_queryset(self):
        salesman_id = self.kwargs.get('pk')
        salesman = User.objects.get(pk=salesman_id)
        start_date, end_date = self.get_start_end_dates()
        return get_salesman_orders(salesman, start_date, end_date)


class SalesmenReportDetailView(DateTimeRangeFilterMixin, RetrieveAPIView):
    queryset = User.objects.all()

    def retrieve(self, request, *args, **kwargs):
        salesman = self.get_object()
        start_date, end_date = self.get_start_end_dates()

        orders = get_salesman_orders(salesman, start_date, end_date)
        payments = get_worker_payments(salesman, start_date, end_date)
        incomes = get_worker_incomes(salesman, start_date, end_date)
        incomes_for_orders = incomes.filter(reason=WorkerIncomeReason.PRODUCT_SALE)
        incomes_for_factories = incomes.filter(
            reason__in=[WorkerIncomeReason.PRODUCT_FACTORY_CREATE, WorkerIncomeReason.PRODUCT_FACTORY_SALE]
        )

        salesman.orders_count = orders.count()
        salesman.order_total_sum = orders.aggregate(total_sum=models.Sum('total_with_discount', default=0))['total_sum']
        salesman.payment_sum = self.calculate_payment_sum(payments)
        salesman.income_sum = self.calculate_income_sum(incomes)
        salesman.income_for_orders_sum = self.calculate_income_sum(incomes_for_orders)
        salesman.income_for_factories_sum = self.calculate_income_sum(incomes_for_factories)
        serializer = SalesmenReportDetailSerializer(
            instance=salesman,
        )
        return Response(serializer.data)

    def calculate_income_sum(self, incomes):
        income_in = incomes.filter(income_type=WorkerIncomeType.INCOME).aggregate(
            total_sum=models.Sum('total', default=0)
        )['total_sum']
        income_out = incomes.filter(income_type=WorkerIncomeType.OUTCOME).aggregate(
            total_sum=models.Sum('total', default=0)
        )['total_sum']
        return income_in - income_out

    def calculate_payment_sum(self, payments):
        payment_in = payments.filter(payment_type=PaymentType.INCOME).aggregate(
            total_sum=models.Sum('amount', default=0)
        )['total_sum']
        payment_out = payments.filter(payment_type=PaymentType.OUTCOME).aggregate(
            total_sum=models.Sum('amount', default=0)
        )['total_sum']
        return payment_out - payment_in


# =================== OtherWorkerReport =================== #
class OtherWorkersReportListView(DateTimeRangeFilterMixin, ListAPIView):
    serializer_class = OtherWorkersReportListSerializer
    pagination_class = CustomPagination
    filter_backends = [
        filters.SearchFilter
    ]
    search_fields = [
        'first_name',
        'last_name',
        'industry__name'
    ]

    def get_queryset(self):
        start_date, end_date = self.get_start_end_dates()
        return get_other_worker_list(self.request, start_date, end_date)


class OtherWorkersReportSummaryView(DateTimeRangeFilterMixin, ExportDisablePermissionMixin, ViewSet):
    def get_queryset(self):
        start_date, end_date = self.get_start_end_dates()
        return get_other_worker_list(self.request, start_date, end_date)

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('start_date', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description="Start date in DD.MM.YYYY HH:MM format"),
            openapi.Parameter('end_date', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description="End date in DD.MM.YYYY HH:MM format"),
        ]
    )
    def list(self, request, *args, **kwargs):
        other_workers_list = self.get_queryset()
        aggregated_data = self.get_aggregated_data(other_workers_list)
        serializer = OtherWorkersReportSummarySerializer(instance={**aggregated_data})
        return Response(serializer.data)

    def get_aggregated_data(self, salesmen):
        # total_income_sum = salesmen.aggregate(total_income_sum=models.Sum('income_sum'))['total_income_sum']
        total_payments_sum = salesmen.aggregate(total_payment_sum=models.Sum('payment_sum'))['total_payment_sum']

        return {
            # 'total_income_sum': total_income_sum,
            'total_payments_sum': total_payments_sum,
        }

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('start_date', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description="Start date in DD.MM.YYYY HH:MM format"),
            openapi.Parameter('end_date', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description="End date in DD.MM.YYYY HH:MM format"),
        ]
    )
    def get_excel_report(self, request, *args, **kwargs):
        start_date, end_date = self.get_start_end_dates()
        self.request.user = User.objects.get(pk=kwargs['user_id'])
        worker_list = self.get_queryset()
        aggregated_data = self.get_aggregated_data(worker_list)
        byte_buffer = OtherWorkersReportExcelExport(worker_list, aggregated_data, start_date, end_date).get_excel_file()
        return FileResponse(byte_buffer, filename='Sotrudniki_otchet.xlsx', as_attachment=True)


class OtherWorkerReportDetailView(DateTimeRangeFilterMixin, RetrieveAPIView):
    queryset = User.objects.all()

    def retrieve(self, request, *args, **kwargs):
        worker = self.get_object()
        start_date, end_date = self.get_start_end_dates()

        payments = get_worker_payments(worker, start_date, end_date)

        worker.payment_sum = self.calculate_payment_sum(payments)
        serializer = OtherWorkersReportListSerializer(
            instance=worker,
        )
        return Response(serializer.data)

    def calculate_payment_sum(self, payments):
        payment_in = payments.filter(payment_type=PaymentType.INCOME).aggregate(
            total_sum=models.Sum('amount', default=0)
        )['total_sum']
        payment_out = payments.filter(payment_type=PaymentType.OUTCOME).aggregate(
            total_sum=models.Sum('amount', default=0)
        )['total_sum']
        return payment_out - payment_in


# =================== FloristsReport =================== #

class FloristsReportFloristListView(DateTimeRangeFilterMixin, IndustryFilterMixin, ListAPIView):
    queryset = User.objects.all()
    serializer_class = FloristsReportFloristListSerializer
    pagination_class = CustomPagination
    filter_backends = [
        filters.SearchFilter
    ]
    search_fields = [
        'first_name',
        'last_name',
    ]

    def get_queryset(self):
        start_date, end_date = self.get_start_end_dates()
        industry = self.request.query_params.getlist('industry')

        return get_florist_list(self.request, start_date, end_date, industry)


class FloristsReportSummaryView(DateTimeRangeFilterMixin, IndustryFilterMixin, ExportDisablePermissionMixin, ViewSet):

    def get_queryset(self):
        start_date, end_date = self.get_start_end_dates()
        industry = self.request.query_params.getlist('industry')
        return get_florist_list(self.request, start_date, end_date, industry)

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('start_date', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description="Start date in DD.MM.YYYY format"),
            openapi.Parameter('end_date', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description="End date in DD.MM.YYYY format"),
        ]
    )
    def list(self, request, *args, **kwargs):
        start_date, end_date = self.get_start_end_dates()
        florist = self.get_queryset()
        aggregated_data = self.get_aggregated_data(florist)

        serializer = FloristReportSummarySerializer(instance={**aggregated_data})
        return Response(serializer.data)

    def get_aggregated_data(self, florists):
        aggregations = florists.aggregate(
            total_sold_product_count=models.Sum('sold_product_count', default=0),
            total_finished_product_count=models.Sum('finished_product_count', default=0),
            total_written_off_product_count=models.Sum('written_off_product_count', default=0),
            total_income_sum=models.Sum('income_sum', default=0),
            total_payment_sum=models.Sum('payment_sum', default=0)
        )

        total_sold_product_count = aggregations['total_sold_product_count']
        total_finished_product_count = aggregations['total_finished_product_count']
        total_written_off_product_count = aggregations['total_written_off_product_count']
        total_product_count = (
                total_sold_product_count +
                total_finished_product_count +
                total_written_off_product_count
        )

        total_income_sum = aggregations['total_income_sum']
        total_payment_sum = aggregations['total_payment_sum']

        return {
            "total_sold_product_count": total_sold_product_count,
            "total_finished_product_count": total_finished_product_count,
            "total_written_off_product_count": total_written_off_product_count,
            "total_product_count": total_product_count,
            "total_income_sum": total_income_sum,
            "total_payment_sum": total_payment_sum,
        }

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('start_date', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description="Start date in DD.MM.YYYY format"),
            openapi.Parameter('end_date', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description="End date in DD.MM.YYYY format"),
        ]
    )
    def get_excel_report(self, request, *args, **kwargs):
        start_date, end_date = self.get_start_end_dates()
        self.request.user = User.objects.get(pk=kwargs['user_id'])
        florist_list = self.get_queryset()
        aggregated_data = self.get_aggregated_data(florist_list)
        byte_buffer = FloristReportExcelExport(florist_list, aggregated_data, start_date, end_date).get_excel_file()
        return FileResponse(byte_buffer, filename='Florist_report.xlsx', as_attachment=True)


class FloristReportProductFactoryListView(DateTimeRangeFilterMixin, ListAPIView):
    serializer_class = FloristReportProductFactorySerializer
    pagination_class = CustomPagination
    filter_backends = [
        filters.SearchFilter
    ]
    search_fields = [
        'name',
    ]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('start_date', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description="Start date in DD.MM.YYYY format"),
            openapi.Parameter('end_date', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description="End date in DD.MM.YYYY format"),
            openapi.Parameter('status', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              enum=ProductFactoryStatus.values),
        ]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        start_date, end_date = self.get_start_end_dates()
        status = self.request.query_params.getlist('status')

        florist_id = self.kwargs.get('pk')
        florist = get_object_or_404(User, pk=florist_id)

        return get_florist_product_factories(florist, status, start_date, end_date)


class FloristReportDetailView(DateTimeRangeFilterMixin, RetrieveAPIView):
    queryset = User.objects.all()

    def retrieve(self, request, *args, **kwargs):
        start_date, end_date = self.get_start_end_dates()
        status = self.request.query_params.getlist('status')
        florist = self.get_object()

        products = get_florist_product_factories(florist, status, start_date, end_date)
        sold_products = products.filter(status=ProductFactoryStatus.SOLD)
        finished_products = products.filter(status__in=[ProductFactoryStatus.FINISHED, ProductFactoryStatus.PENDING])
        written_off_products = products.filter(status=ProductFactoryStatus.WRITTEN_OFF)
        payments = get_worker_payments(florist, start_date, end_date)
        incomes = get_worker_incomes(florist, start_date, end_date)
        incomes_for_orders = incomes.filter(reason=WorkerIncomeReason.PRODUCT_SALE)
        incomes_for_factories = incomes.filter(
            reason__in=[WorkerIncomeReason.PRODUCT_FACTORY_CREATE, WorkerIncomeReason.PRODUCT_FACTORY_SALE]
        )

        florist.sold_product_count = sold_products.count()
        florist.finished_product_count = finished_products.count()
        florist.written_off_product_count = written_off_products.count()
        florist.total_product_count = florist.finished_product_count \
                                      + florist.sold_product_count \
                                      + florist.written_off_product_count
        florist.payment_sum = self.calculate_payment_sum(payments)
        florist.income_sum = self.calculate_income_sum(incomes)
        florist.income_for_orders_sum = self.calculate_income_sum(incomes_for_orders)
        florist.income_for_factories_sum = self.calculate_income_sum(incomes_for_factories)

        serializer = FloristReportDetailSerializer(instance=florist)
        return Response(serializer.data, status=200)

    def calculate_income_sum(self, incomes):
        income_in = incomes.filter(income_type=WorkerIncomeType.INCOME).aggregate(
            total_sum=models.Sum('total', default=0)
        )['total_sum']
        income_out = incomes.filter(income_type=WorkerIncomeType.OUTCOME).aggregate(
            total_sum=models.Sum('total', default=0)
        )['total_sum']
        return income_in - income_out

    def calculate_payment_sum(self, payments):
        payment_in = payments.filter(payment_type=PaymentType.INCOME).aggregate(
            total_sum=models.Sum('amount', default=0)
        )['total_sum']
        payment_out = payments.filter(payment_type=PaymentType.OUTCOME).aggregate(
            total_sum=models.Sum('amount', default=0)
        )['total_sum']
        return payment_out - payment_in


# ================== WorkersReport ================== #
class WorkersReportWorkerListView(DateTimeRangeFilterMixin, IndustryFilterMixin, ListAPIView):
    queryset = User.objects.all()
    serializer_class = WorkersReportWorkerListSerializer
    pagination_class = CustomPagination
    filter_backends = [
        filters.SearchFilter,
        DjangoFilterBackend
    ]
    filterset_class = WorkersFilter
    search_fields = [
        'first_name',
        'last_name',
    ]

    def get_queryset(self):
        start_date, end_date = self.get_start_end_dates()
        industry = self.request.query_params.getlist('industry')

        return get_worker_list(start_date, end_date, industry)

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('start_date', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description="Start date in DD.MM.YYYY HH:mm format"),
            openapi.Parameter('end_date', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description="End date in DD.MM.YYYY HH:mm format"),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class WorkersReportSummaryView(DateTimeRangeFilterMixin, IndustryFilterMixin, ExportDisablePermissionMixin, ViewSet):

    def get_queryset(self):
        start_date, end_date = self.get_start_end_dates()
        industry = self.request.query_params.getlist('industry')
        return get_worker_list(start_date, end_date, industry)

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('start_date', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description="Start date in DD.MM.YYYY HH:mm format"),
            openapi.Parameter('end_date', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description="End date in DD.MM.YYYY HH:mm format"),
            openapi.Parameter('industry', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description="Industry"),
            openapi.Parameter('worker_type', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              enum=UserType.values)
        ]
    )
    def list(self, request, *args, **kwargs):
        workers = WorkersFilter(request.query_params, self.get_queryset()).qs
        aggregated_data = self.get_aggregated_data(workers)

        serializer = WorkersReportSummarySerializer(instance={**aggregated_data, 'workers': workers})
        return Response(serializer.data)

    def get_aggregated_data(self, workers):
        aggregations = workers.aggregate(
            total_orders=models.Sum('orders_count', default=0),
            total_orders_sum=models.Sum('order_total_sum', default=0),
            total_income_sum=models.Sum('income_sum', default=0),
            total_payment_sum=models.Sum('payment_sum', default=0),
            total_sold_product_count=models.Sum('sold_product_count', default=0),
            total_finished_product_count=models.Sum('finished_product_count', default=0),
            total_written_off_product_count=models.Sum('written_off_product_count', default=0)
        )

        total_orders_count = aggregations['total_orders']
        total_orders_sum = aggregations['total_orders_sum']
        total_income_sum = aggregations['total_income_sum']
        total_payments_sum = aggregations['total_payment_sum']
        total_sold_product_count = aggregations['total_sold_product_count']
        total_finished_product_count = aggregations['total_finished_product_count']
        total_written_off_product_count = aggregations['total_written_off_product_count']
        total_product_count = total_sold_product_count + total_finished_product_count + total_written_off_product_count

        return {
            'total_orders_count': total_orders_count,
            'total_orders_sum': total_orders_sum,
            "total_sold_product_count": total_sold_product_count,
            "total_finished_product_count": total_finished_product_count,
            "total_written_off_product_count": total_written_off_product_count,
            "total_product_count": total_product_count,
            'total_income_sum': total_income_sum,
            'total_payments_sum': total_payments_sum,
        }

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('start_date', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description="Start date in DD.MM.YYYY format"),
            openapi.Parameter('end_date', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description="End date in DD.MM.YYYY format"),
            openapi.Parameter('industry', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description="Industry"),
            openapi.Parameter('worker_type', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              enum=UserType.values)
        ]
    )
    def get_excel_report(self, request, *args, **kwargs):
        start_date, end_date = self.get_start_end_dates()
        self.request.user = User.objects.get(pk=kwargs['user_id'])
        workers_list = self.get_queryset()
        aggregated_data = self.get_aggregated_data(workers_list)
        byte_buffer = WorkersReportExcelExport(workers_list, aggregated_data, start_date, end_date).get_excel_file()
        return FileResponse(byte_buffer, filename='sotrudniki_otchet.xlsx', as_attachment=True)


class WorkersReportDetailView(DateTimeRangeFilterMixin, RetrieveAPIView):
    queryset = User.objects.all()

    def retrieve(self, request, *args, **kwargs):
        start_date, end_date = self.get_start_end_dates()
        status = self.request.query_params.getlist('status')
        worker = self.get_object()

        orders = get_salesman_orders(worker, start_date, end_date)
        products = get_florist_product_factories(worker, status, start_date, end_date)
        sold_products = products.filter(status=ProductFactoryStatus.SOLD)
        finished_products = products.filter(status__in=[ProductFactoryStatus.FINISHED, ProductFactoryStatus.PENDING])
        written_off_products = products.filter(status=ProductFactoryStatus.WRITTEN_OFF)
        payments = get_worker_payments(worker, start_date, end_date)
        incomes = get_worker_incomes(worker, start_date, end_date)
        incomes_for_orders = incomes.filter(reason=WorkerIncomeReason.PRODUCT_SALE)
        incomes_for_factories = incomes.filter(
            reason__in=[WorkerIncomeReason.PRODUCT_FACTORY_CREATE, WorkerIncomeReason.PRODUCT_FACTORY_SALE]
        )

        worker.orders_count = orders.count()
        worker.order_total_sum = orders.aggregate(total_sum=models.Sum('total_with_discount', default=0))['total_sum']
        worker.sold_product_count = sold_products.count()
        worker.finished_product_count = finished_products.count()
        worker.written_off_product_count = written_off_products.count()
        worker.total_product_count = worker.finished_product_count \
                                     + worker.sold_product_count \
                                     + worker.written_off_product_count
        worker.payment_sum = self.calculate_payment_sum(payments)
        worker.income_sum = self.calculate_income_sum(incomes)
        worker.income_for_orders_sum = self.calculate_income_sum(incomes_for_orders)
        worker.income_for_factories_sum = self.calculate_income_sum(incomes_for_factories)

        serializer = WorkersReportDetailSerializer(instance=worker)
        return Response(serializer.data, status=200)

    def calculate_income_sum(self, incomes):
        income_in = incomes.filter(income_type=WorkerIncomeType.INCOME).aggregate(
            total_sum=models.Sum('total', default=0)
        )['total_sum']
        income_out = incomes.filter(income_type=WorkerIncomeType.OUTCOME).aggregate(
            total_sum=models.Sum('total', default=0)
        )['total_sum']
        return income_in - income_out

    def calculate_payment_sum(self, payments):
        payment_in = payments.filter(payment_type=PaymentType.INCOME).aggregate(
            total_sum=models.Sum('amount', default=0)
        )['total_sum']
        payment_out = payments.filter(payment_type=PaymentType.OUTCOME).aggregate(
            total_sum=models.Sum('amount', default=0)
        )['total_sum']
        return payment_out - payment_in


class WorkersTypeOptionsView(APIView):
    def get(self, request, *args, **kwargs):
        allowed_labels = [
            UserType.FLORIST,
            UserType.FLORIST_PERCENT,
            UserType.FLORIST_ASSISTANT,
            UserType.SALESMAN,
            UserType.NO_BONUS_SALESMAN,
            UserType.MANAGER,
        ]
        worker_type_options = [{'value': k, 'label': v} for k, v in UserType.choices if k in allowed_labels]
        return Response(worker_type_options)


# =================== WriteOffsReport =================== #
class WriteOffReportProductsListView(ReportCommonFiltersMixin, ListAPIView):
    queryset = Product.objects.get_available()
    serializer_class = WriteOffsReportProductListSerializer
    pagination_class = CustomPagination
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter
    ]
    filterset_class = WriteOffReportProductFilter
    search_fields = [
        'name',
        'category__name'
    ]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('start_date', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description="Start date in DD.MM.YYYY format"),
            openapi.Parameter('end_date', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description="End date in DD.MM.YYYY format"),
            openapi.Parameter('industry', in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER),
            openapi.Parameter('category', in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER),
            openapi.Parameter('page', in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER),
        ]
    )
    def get(self, request):
        return super().get(request)

    def get_queryset(self):
        start_date, end_date = self.get_start_end_dates()

        qs = get_write_offs_report_products(self.request, start_date, end_date)
        return qs


class WriteOffsReportProductFactoriesListView(ReportCommonFiltersMixin, ListAPIView):
    queryset = ProductFactory.objects.get_available()
    serializer_class = WriteOffsReportProductFactoryListSerializer
    pagination_class = CustomPagination
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter
    ]
    filterset_class = WriteOffReportProductFactoryFilter
    search_fields = [
        'name',
        'category__name'
    ]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('page', in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER),
            openapi.Parameter('start_date', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description="Start date in DD.MM.YYYY format"),
            openapi.Parameter('end_date', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description="End date in DD.MM.YYYY format"),
            openapi.Parameter('factory_category', in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER),
        ]
    )
    def get(self, request):
        return super().get(request)

    def get_queryset(self):
        start_date, end_date = self.get_start_end_dates()
        qs = get_write_offs_report_product_factories(self.request, start_date, end_date)
        return qs


class WriteOffReportSummaryView(ReportCommonFiltersMixin, ExportDisablePermissionMixin, ViewSet):
    products_filterset_class = WriteOffReportProductFilter
    product_factories_filterset_class = WriteOffReportProductFactoryFilter

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('start_date', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description="Start date in DD.MM.YYYY format"),
            openapi.Parameter('end_date', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description="End date in DD.MM.YYYY format"),
            openapi.Parameter('industry', in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER),
            openapi.Parameter('category', in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER),
            openapi.Parameter('factory_category', in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER),
        ]
    )
    def list(self, request, *args, **kwargs):
        start_date, end_date = self.get_start_end_dates()
        products = get_write_offs_report_products(request, start_date, end_date)
        product_factories = get_write_offs_report_product_factories(request, start_date, end_date)
        products = self.products_filterset_class(request.query_params, products).qs
        product_factories = self.product_factories_filterset_class(request.query_params, product_factories).qs
        data = self.get_aggregated_data(products, product_factories)

        serializer = WriteOffsReportSummarySerializer(data)
        return Response(serializer.data)

    def get_aggregated_data(self, products, product_factories):
        product_aggregations = products.aggregate(
            total_product_count=models.Sum('product_count', default=0, output_field=models.DecimalField()),
            total_self_price_sum=models.Sum(models.F('self_price_sum'), default=0, output_field=models.DecimalField())
        )

        product_factory_aggregations = product_factories.aggregate(
            total_self_price_sum=models.Sum(models.F('self_price'), default=0, output_field=models.DecimalField())
        )

        total_product_count = product_aggregations['total_product_count']
        total_self_price_sum = product_aggregations['total_self_price_sum']
        total_product_factory_count = Decimal(product_factories.count())
        total_product_factory_self_price_sum = product_factory_aggregations['total_self_price_sum']

        total_count = total_product_count + total_product_factory_count
        total_self_price = total_self_price_sum + total_product_factory_self_price_sum
        return {
            'total_product_count': total_product_count,
            'total_self_price_sum': total_self_price_sum,
            'total_product_factory_count': total_product_factory_count,
            'total_product_factory_self_price_sum': total_product_factory_self_price_sum,
            'total_count': total_count,
            'total_self_price': total_self_price,
        }

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('start_date', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description="Start date in DD.MM.YYYY format"),
            openapi.Parameter('end_date', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description="End date in DD.MM.YYYY format"),
            openapi.Parameter('industry', in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER),
            openapi.Parameter('category', in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER),
            openapi.Parameter('factory_category', in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER),
        ]
    )
    def get_excel_report(self, request, *args, **kwargs):
        start_date, end_date = self.get_start_end_dates()
        self.request.user = User.objects.get(pk=kwargs['user_id'])
        products = get_write_offs_report_products(request, start_date, end_date)
        product_factories = get_write_offs_report_product_factories(request, start_date, end_date)
        products = self.products_filterset_class(request.query_params, products).qs
        product_factories = self.product_factories_filterset_class(request.query_params, product_factories).qs
        aggregated_data = self.get_aggregated_data(products, product_factories)
        byte_buffer = WriteOffReportExcelExport(products, product_factories, aggregated_data, start_date,
                                                end_date).get_excel_file()
        return FileResponse(byte_buffer, filename='Spisaniya_otchet.xlsx', as_attachment=True)


class WriteOffReportWriteOffListView(DateRangeFilterMixin, ListAPIView):
    serializer_class = WriteOffsReportProductWriteOffSerializer
    pagination_class = CustomPagination
    filter_backends = [
        filters.SearchFilter
    ]
    search_fields = ['comment']

    def get_queryset(self):
        start_date, end_date = self.get_start_end_dates()
        product_id = self.kwargs.get('pk')
        product = get_object_or_404(Product, pk=product_id)
        return get_product_write_offs(self.request, product, start_date, end_date)


class WriteOffsReportDetailView(DateRangeFilterMixin, RetrieveAPIView):
    queryset = Product.objects.get_available().select_related('category__industry')

    def retrieve(self, request, *args, **kwargs):
        product = self.get_object()
        product_write_offs = self.get_product_write_offs(product)

        product.product_count = product_write_offs.aggregate(total_count=models.Sum('count', default=0))['total_count']
        product.self_price_sum = product_write_offs.aggregate(
            self_price_sum=models.Sum(models.F('count') * models.F('warehouse_product__self_price'), default=0)
        )['self_price_sum']

        serializer = WriteOffsReportProductListSerializer(instance=product)
        return Response(serializer.data)

    def get_product_write_offs(self, product):
        start_date, end_date = self.get_start_end_dates()
        return WarehouseProductWriteOff.objects.get_available().filter(
            warehouse_product__product=product,
            created_at__gte=start_date,
            created_at__lte=end_date
        ).select_related('warehouse_product', 'created_user')


# =================== ClientsReport =================== #
class ClientsReportView(ReportCommonFiltersMixin, ExportDisablePermissionMixin, ModelViewSet):
    queryset = Client.objects.get_available()
    serializer_class = ClientsReportSerializer
    pagination_class = CustomPagination
    filter_backends = [
        filters.SearchFilter
    ]
    search_fields = ['comment', 'phone_number', 'full_name']

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('start_date', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description="Start date in DD.MM.YYYY format"),
            openapi.Parameter('end_date', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description="End date in DD.MM.YYYY format"),
            openapi.Parameter('has_debt', in_=openapi.IN_QUERY, type=openapi.TYPE_BOOLEAN),
        ]
    )
    def get(self, request):
        return super().get(request)

    def get_queryset(self):
        qs = super().get_queryset()
        start_date, end_date = self.get_start_end_dates()
        has_debt = self.request.query_params.get('has_debt', None)

        qs = qs.annotate(
            debt=get_client_debt(start_date, end_date),
            orders_count=get_client_orders_count(start_date, end_date),
            orders_sum=get_client_orders_sum(start_date, end_date),
            total_discount_sum=get_client_orders_discount_sum(start_date, end_date)
        ).order_by('-orders_count')

        if has_debt is not None:
            if has_debt == 'true':
                qs = qs.exclude(debt=0)
            else:
                qs = qs.filter(debt=0)
        return qs

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('start_date', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description="Start date in DD.MM.YYYY format"),
            openapi.Parameter('end_date', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description="End date in DD.MM.YYYY format"),
            openapi.Parameter('has_debt', in_=openapi.IN_QUERY, type=openapi.TYPE_BOOLEAN),
        ]
    )
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        aggregated_date = self.get_aggregated_data(queryset)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.serializer_class(dict(clients=page, **aggregated_date))
            return self.get_paginated_response(serializer.data)

        serializer = self.serializer_class(dict(clients=queryset, **aggregated_date))
        return Response(serializer.data)

    def get_aggregated_data(self, qs: QuerySet):
        aggregations = qs.aggregate(
            total_debt=models.Sum('debt', default=0),
            total_orders_count=models.Sum('orders_count', default=0),
            total_orders_sum=models.Sum('orders_sum', default=0)
        )

        total_debt = aggregations['total_debt']
        total_orders_count = aggregations['total_orders_count']
        total_orders_sum = aggregations['total_orders_sum']
        return {
            'total_debt': total_debt,
            'total_orders_count': total_orders_count,
            'total_orders_sum': total_orders_sum,
        }

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('start_date', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description="Start date in DD.MM.YYYY format"),
            openapi.Parameter('end_date', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description="End date in DD.MM.YYYY format"),
            openapi.Parameter('has_debt', in_=openapi.IN_QUERY, type=openapi.TYPE_BOOLEAN),
        ]
    )
    def get_excel_report(self, request, *args, **kwargs):
        start_date, end_date = self.get_start_end_dates()
        self.request.user = User.objects.get(pk=kwargs['user_id'])
        clients = self.filter_queryset(self.get_queryset())
        aggregated_data = self.get_aggregated_data(clients)
        byte_buffer = ClientsReportExcelExport(clients, aggregated_data, start_date, end_date).get_excel_file()
        return FileResponse(byte_buffer, filename='Klient_otchet.xlsx', as_attachment=True)


class ClientsReportOrderListView(ReportCommonFiltersMixin, ListAPIView):
    serializer_class = ClientsReportOrderSerializer
    pagination_class = CustomPagination
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter
    ]
    # filterset_class = OrderFilter
    search_fields = ['id']

    def get_queryset(self):
        industry = self.request.query_params.getlist('industry')
        start_date, end_date = self.get_start_end_dates()
        client_id = self.kwargs.get('pk')
        client = get_object_or_404(Client, pk=client_id)
        orders = get_clients_orders(self.request, client, start_date, end_date)
        if industry:
            orders.by_industries(industry)
        return orders


class ClientsReportDetailView(ReportCommonFiltersMixin, RetrieveAPIView):
    queryset = Client.objects.get_available()
    serializer_class = ClientsReportClientListSerializer

    order_filterset_class = OrderFilter

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('start_date', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description="Start date in DD.MM.YYYY format"),
            openapi.Parameter('end_date', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description="End date in DD.MM.YYYY format"),
            openapi.Parameter('industry', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING),
            # openapi.Parameter('status', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING, enum=OrderStatus.values),
        ]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        industry = self.request.query_params.getlist('industry')
        start_date, end_date = self.get_start_end_dates()
        client = self.get_object()
        orders = get_clients_orders(self.request, client, start_date, end_date)
        if industry:
            orders.by_industries(industry)

        client.orders_count = orders.count()
        client.orders_sum = orders.aggregate(total_sum=models.Sum('total_with_discount', default=0))['total_sum']
        client.debt = orders.aggregate(debt=models.Sum('debt', default=0))['debt']
        client.total_discount_sum = orders.aggregate(
            total_discount_sum=models.Sum('total_discount', default=0))['total_discount_sum']

        serializer = ClientsReportClientListSerializer(
            instance=client,
        )
        return Response(serializer.data)


# =================== ProductFactoriesReport =================== #
class ProductFactoriesReportProductFactoryListView(ReportCommonFiltersMixin, ListAPIView):
    queryset = ProductFactory.objects.get_available()
    serializer_class = ProductFactoriesReportProductListSerializer
    pagination_class = CustomPagination
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter
    ]
    filterset_class = ProductFactoriesReportProductFactoryFilter
    search_fields = ['name']

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('start_date', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description="Start date in DD.MM.YYYY format"),
            openapi.Parameter('end_date', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description="End date in DD.MM.YYYY format"),
            openapi.Parameter('category', in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER),
            openapi.Parameter('florist', in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER),
            openapi.Parameter('status', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              enum=ProductFactoryStatus.values),
        ]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        start_date, end_date = self.get_start_end_dates()

        qs = get_factories_report_product_factories(self.request, start_date, end_date)
        return qs


class ProductFactoriesReportSummaryView(ReportCommonFiltersMixin, ExportDisablePermissionMixin, ViewSet):
    filterset_class = ProductFactoriesReportProductFactoryFilter

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('start_date', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description="Start date in DD.MM.YYYY format"),
            openapi.Parameter('end_date', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description="End date in DD.MM.YYYY format"),
            openapi.Parameter('category', in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER),
            openapi.Parameter('florist', in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER),
            openapi.Parameter('status', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              enum=ProductFactoryStatus.values),
            openapi.Parameter('sales_type', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              enum=ProductFactorySalesType.values),
        ]
    )
    def list(self, request, *args, **kwargs):
        start_date, end_date = self.get_start_end_dates()
        product_factories = get_factories_report_product_factories(request, start_date, end_date)
        finished_products = product_factories.filter(
            status__in=[ProductFactoryStatus.FINISHED, ProductFactoryStatus.PENDING]
        )
        sold_products = product_factories.filter(
            status=ProductFactoryStatus.SOLD
        )
        written_off_products = product_factories.filter(
            status=ProductFactoryStatus.WRITTEN_OFF
        )

        finished_products = self.filterset_class(data=request.query_params, queryset=finished_products).qs
        sold_products = self.filterset_class(data=request.query_params, queryset=sold_products).qs
        written_off_products = self.filterset_class(data=request.query_params, queryset=written_off_products).qs

        data = self.get_aggregated_data(finished_products, sold_products, written_off_products)
        serializer = ProductFactoriesReportSummarySerializer(data)

        return Response(serializer.data)

    def get_aggregated_data(self, finished_products, sold_products, written_off_products):
        # Aggregations for finished products
        finished_aggregations = finished_products.aggregate(
            total_finished_self_price=models.Sum('self_price', default=0),
            total_finished_price=models.Sum('price', default=0)
        )
        total_finished_count = finished_products.count()

        # Aggregations for sold products
        sold_aggregations = sold_products.aggregate(
            total_sold_self_price=models.Sum('self_price', default=0),
            total_sold_price=models.Sum('price', default=0),
            total_sale_sum=models.Sum('sold_price', default=0)
        )
        total_sold_count = sold_products.count()

        # Aggregations for written off products
        written_off_aggregations = written_off_products.aggregate(
            total_written_off_self_price=models.Sum('self_price', default=0),
            total_written_off_price=models.Sum('price', default=0)
        )
        total_written_off_count = written_off_products.count()

        # Combining results
        total_finished_self_price = finished_aggregations['total_finished_self_price']
        total_finished_price = finished_aggregations['total_finished_price']

        total_sold_self_price = sold_aggregations['total_sold_self_price']
        total_sold_price = sold_aggregations['total_sold_price']
        total_sale_sum = sold_aggregations['total_sale_sum']

        total_written_off_self_price = written_off_aggregations['total_written_off_self_price']
        total_written_off_price = written_off_aggregations['total_written_off_price']

        total_product_count = total_finished_count + total_sold_count + total_written_off_count
        total_product_price = total_finished_price + total_sold_price + total_written_off_price
        total_product_self_price = total_sold_self_price + total_finished_self_price + total_written_off_self_price
        return {
            'total_finished_self_price': total_finished_self_price,
            'total_finished_price': total_finished_price,
            'total_finished_count': total_finished_count,
            'total_sold_self_price': total_sold_self_price,
            'total_sold_price': total_sold_price,
            'total_sold_count': total_sold_count,
            'total_written_off_self_price': total_written_off_self_price,
            'total_written_off_price': total_written_off_price,
            'total_written_off_count': total_written_off_count,
            'total_product_count': total_product_count,
            'total_product_price': total_product_price,
            'total_product_self_price': total_product_self_price,
            'total_sale_sum': total_sale_sum,
        }

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('start_date', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description="Start date in DD.MM.YYYY format"),
            openapi.Parameter('end_date', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description="End date in DD.MM.YYYY format"),
            openapi.Parameter('category', in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER),
            openapi.Parameter('florist', in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER),
            openapi.Parameter('status', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              enum=ProductFactoryStatus.values),
        ]
    )
    def get_excel_report(self, request, *args, **kwargs):
        start_date, end_date = self.get_start_end_dates()
        self.request.user = User.objects.get(pk=kwargs['user_id'])
        finished_products = get_factories_report_product_factories(request, start_date, end_date).filter(
            status__in=[ProductFactoryStatus.FINISHED, ProductFactoryStatus.PENDING]
        )
        sold_products = get_factories_report_product_factories(request, start_date, end_date).filter(
            status=ProductFactoryStatus.SOLD
        )
        written_off_products = get_factories_report_product_factories(request, start_date, end_date).filter(
            status=ProductFactoryStatus.WRITTEN_OFF
        )

        finished_products = self.filterset_class(data=request.query_params, queryset=finished_products).qs
        sold_products = self.filterset_class(data=request.query_params, queryset=sold_products).qs
        written_off_products = self.filterset_class(data=request.query_params, queryset=written_off_products).qs

        data = self.get_aggregated_data(finished_products, sold_products, written_off_products)
        byte_buffer = ProductFactoryReportExcelExport(finished_products, sold_products, written_off_products, data,
                                                      start_date, end_date).get_excel_file()
        return FileResponse(byte_buffer, filename='Buket_otchet.xlsx', as_attachment=True)


# =================== ProductReturnsReport =================== #
class ProductReturnsReportProductReturnListView(ReportCommonFiltersMixin, ListAPIView):
    serializer_class = ProductReturnsReportProductReturnListSerializer
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter
    ]
    filterset_class = OrderItemReturnFilter
    pagination_class = CustomPagination
    search_fields = ['order_item__product__name', 'order__id']

    def get_queryset(self):
        start_date, end_date = self.get_start_end_dates()
        product_returns = get_returns_report_product_returns(start_date, end_date)
        return product_returns


class ProductReturnsReportFactoriesListView(ReportCommonFiltersMixin, ListAPIView):
    serializer_class = ProductReturnsReportProductFactoryReturnListSerializer
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter
    ]
    filterset_class = OrderItemProductFactoryReturnFilter
    pagination_class = CustomPagination
    search_fields = ['product_factory__name', 'order__id']

    def get_queryset(self):
        start_date, end_date = self.get_start_end_dates()
        product_returns = get_returns_report_factories_returns(start_date, end_date)
        return product_returns


class ProductReturnsReportSummaryView(ReportCommonFiltersMixin, ExportDisablePermissionMixin, ViewSet):
    pagination_class = CustomPagination

    def get_filtered_queryset(self, queryset, filterset_class):
        return filterset_class(self.request.query_params, queryset=queryset).qs

    def get_querysets(self):
        start_date, end_date = self.get_start_end_dates()
        product_returns = get_returns_report_product_returns(start_date, end_date)
        product_factory_returns = get_returns_report_factories_returns(start_date, end_date)
        product_returns = self.get_filtered_queryset(product_returns, OrderItemReturnFilter)
        product_factory_returns = self.get_filtered_queryset(product_factory_returns,
                                                             OrderItemProductFactoryReturnFilter)

        # if self.request.query_params.get('category'):
        #     product_factory_returns = product_factory_returns.none()
        # if self.request.query_params.get('factory_category'):
        #     product_returns = product_returns.none()
        return product_returns, product_factory_returns

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('start_date', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description="Start date in DD.MM.YYYY format"),
            openapi.Parameter('end_date', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description="End date in DD.MM.YYYY format"),
            openapi.Parameter('industry', in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER),
            openapi.Parameter('category', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING),
            openapi.Parameter('factory_category', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING),
        ]
    )
    def list(self, request, *args, **kwargs):
        product_returns, product_factory_returns = self.get_querysets()
        aggregated_data = self.get_aggregated_data(product_returns, product_factory_returns)

        serializer = ProductReturnsReportSerializer(instance=dict(
            **aggregated_data
        ))

        return Response(serializer.data)

    def get_aggregated_data(self, product_returns, product_factory_returns):
        # Aggregations for product returns
        product_returns_aggregations = product_returns.aggregate(
            total_product_returns=models.Sum('count', default=0),
            total_product_returns_price=models.Sum('total', default=0),
            total_product_returns_self_price=models.Sum('total_self_price', default=0)
        )

        # Aggregations for product factory returns
        product_factory_returns_aggregations = product_factory_returns.aggregate(
            total_product_factory_returns_price=models.Sum('price', default=0),
            total_product_factory_returns_self_price=models.Sum('product_factory__self_price', default=0)
        )

        # Counts
        total_product_returns = product_returns_aggregations['total_product_returns']
        total_product_factory_returns = product_factory_returns.count()

        # Prices
        total_product_returns_price = product_returns_aggregations['total_product_returns_price']
        total_product_returns_self_price = product_returns_aggregations['total_product_returns_self_price']
        total_product_factory_returns_price = product_factory_returns_aggregations[
            'total_product_factory_returns_price']
        total_product_factory_returns_self_price = product_factory_returns_aggregations[
            'total_product_factory_returns_self_price']

        # Totals
        total_returns = total_product_returns + total_product_factory_returns
        total_price = total_product_returns_price + total_product_factory_returns_price
        total_self_price = total_product_returns_self_price + total_product_factory_returns_self_price
        return {
            'total_product_returns': total_product_returns,
            'total_product_returns_price': total_product_returns_price,
            'total_product_returns_self_price': total_product_returns_self_price,
            'total_product_factory_returns': total_product_factory_returns,
            'total_product_factory_returns_price': total_product_factory_returns_price,
            'total_product_factory_returns_self_price': total_product_factory_returns_self_price,
            'total_returns': total_returns,
            'total_price': total_price,
            'total_self_price': total_self_price,
        }

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('start_date', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description="Start date in DD.MM.YYYY format"),
            openapi.Parameter('end_date', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description="End date in DD.MM.YYYY format"),
            openapi.Parameter('industry', in_=openapi.IN_QUERY, type=openapi.TYPE_INTEGER),
            openapi.Parameter('category', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING),
            openapi.Parameter('factory_category', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING),
        ]
    )
    def get_excel_report(self, request, *args, **kwargs):
        start_date, end_date = self.get_start_end_dates()
        self.request.user = User.objects.get(pk=kwargs['user_id'])
        product_returns, product_factory_returns = self.get_querysets()
        aggregated_data = self.get_aggregated_data(product_returns, product_factory_returns)
        byte_buffer = ProductReturnReportExcelExport(product_returns, product_factory_returns, aggregated_data,
                                                     start_date, end_date).get_excel_file()
        return FileResponse(byte_buffer, filename='Vozvrat_otchet.xlsx', as_attachment=True)


# =================== OrderItemsReport =================== #
class OrderItemsReportOrderItemList(DateTimeRangeFilterMixin, ListAPIView):
    serializer_class = OrderItemsReportItemListSerializer
    filter_backends = (
        DjangoFilterBackend,
        filters.SearchFilter
    )
    filterset_class = OrderItemFilter
    pagination_class = CustomPagination
    search_fields = ['product__name']

    def get_queryset(self):
        start_date, end_date = self.get_start_end_dates()
        order_items = get_order_items_report_products(start_date, end_date)
        if self.request.user.type == UserType.MANAGER:
            order_items = order_items.by_industry(self.request.user.industry)
        return order_items


class OrderItemsReportOrderItemFactoryList(DateTimeRangeFilterMixin, ListAPIView):
    serializer_class = OrderItemsReportFactoryItemListSerializer
    filter_backends = (
        DjangoFilterBackend,
        filters.SearchFilter
    )
    filterset_class = OrderItemProductFactoryFilter
    pagination_class = CustomPagination
    search_fields = ['product_factory__name']

    def get_queryset(self):
        start_date, end_date = self.get_start_end_dates()
        order_item_factories = order_items_report_factories(start_date, end_date)
        if self.request.user.type == UserType.MANAGER:
            order_item_factories = order_item_factories.by_industry(self.request.user.industry)
        return order_item_factories


class OrderItemsReport(DateTimeRangeFilterMixin, IndustryFilterMixin, ExportDisablePermissionMixin, ModelViewSet):
    serializer_class = OrderItemsReportSerializer
    pagination_class = CustomPagination
    filter_backends = (
        DjangoFilterBackend,
    )
    order_item_filterset_class = OrderItemFilter
    factory_order_item_filterset_class = OrderItemProductFactoryFilter

    def get_filtered_queryset(self, queryset, filterset_class):
        return filterset_class(self.request.query_params, queryset=queryset).qs

    def get_querysets(self):
        start_date, end_date = self.get_start_end_dates()
        order_item_queryset = get_order_items_report_products(start_date, end_date)
        order_item_factory_queryset = order_items_report_factories(start_date, end_date)
        if self.request.user.type == UserType.MANAGER:
            order_item_queryset = order_item_queryset.by_industry(self.request.user.industry)
            order_item_factory_queryset = order_item_factory_queryset.by_industry(self.request.user.industry)
        return order_item_queryset, order_item_factory_queryset

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('start_date', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description="Start date in DD.MM.YYYY format"),
            openapi.Parameter('end_date', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description="End date in DD.MM.YYYY format"),
            openapi.Parameter('industry', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING),
            openapi.Parameter('product', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING),
            openapi.Parameter('category', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING),
            openapi.Parameter('product_factory', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING),
            openapi.Parameter('factory_category', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING),
            openapi.Parameter('created_user', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING),
            openapi.Parameter('salesman', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING),
            openapi.Parameter('client', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING),
        ]
    )
    def list(self, request, *args, **kwargs):
        order_items, order_item_product_factories = self.get_querysets()
        order_items = self.get_filtered_queryset(order_items, self.order_item_filterset_class)
        order_item_product_factories = self.get_filtered_queryset(
            order_item_product_factories,
            self.factory_order_item_filterset_class
        )
        aggregated_data = self.get_aggregated_data(order_items, order_item_product_factories)
        serializer = OrderItemsReportSerializer(instance=aggregated_data)
        return Response(serializer.data)

    def get_aggregated_data(self, order_items, order_item_factories):
        # Aggregations for order_items
        order_items_aggregations = order_items.aggregate(
            total_sale_sum=Sum(F('total') - F('returned_total_sum'), default=0),
            total_sale_sum_without_discount=Sum(
                F('total') + F('total_discount') - F('total_charge') - F('returned_total_sum'), default=0),
            total_count_sum=Sum('count', default=0),
            total_returned_count_sum=Sum('returned_count', default=0),
            total_discount_sum=Sum('total_discount', default=0),
            total_charge_sum=Sum('total_charge', default=0),
            total_self_price_sum=Sum('total_self_price', default=0)
        )

        # Aggregations for order_item_factories
        order_item_factories_aggregations = order_item_factories.aggregate(
            total_sale_sum=Sum(F('total') - F('returned_total_sum'), default=0),
            total_sale_sum_without_discount=Sum(
                F('total') + F('total_discount') - F('total_charge') - F('returned_total_sum'), default=0),
            total_discount_sum=Sum('total_discount', default=0),
            total_charge_sum=Sum('total_charge', default=0),
            total_self_price_sum=Sum('total_self_price', default=0)
        )

        # Counts for order_item_factories
        total_count_sum_factory = order_item_factories.filter(is_returned=False).count()
        total_returned_count_sum_factory = order_item_factories.filter(is_returned=True).count()

        # Summing up the results
        total_sum = order_items_aggregations['total_sale_sum'] + order_item_factories_aggregations['total_sale_sum']
        total_sum_without_discount = order_items_aggregations['total_sale_sum_without_discount'] + \
                                     order_item_factories_aggregations['total_sale_sum_without_discount']
        total_count_sum = order_items_aggregations['total_count_sum'] + total_count_sum_factory
        total_returned_count_sum = order_items_aggregations[
                                       'total_returned_count_sum'] + total_returned_count_sum_factory
        total_discount_sum = order_items_aggregations['total_discount_sum'] + order_item_factories_aggregations[
            'total_discount_sum']
        total_charge_sum = order_items_aggregations['total_charge_sum'] + order_item_factories_aggregations[
            'total_charge_sum']
        total_self_price_sum = order_items_aggregations['total_self_price_sum'] + order_item_factories_aggregations[
            'total_self_price_sum']

        total_profit_sum = total_sum - total_self_price_sum
        return {
            'total_sum': total_sum,
            'total_sum_without_discount': total_sum_without_discount,
            'total_count_sum': total_count_sum,
            'total_returned_count_sum': total_returned_count_sum,
            'total_discount_sum': total_discount_sum,
            'total_charge_sum': total_charge_sum,
            'total_self_price_sum': total_self_price_sum,
            'total_profit_sum': total_profit_sum,
        }

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('start_date', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description="Start date in DD.MM.YYYY format"),
            openapi.Parameter('end_date', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description="End date in DD.MM.YYYY format"),
            openapi.Parameter('industry', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING),
            openapi.Parameter('product', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING),
            openapi.Parameter('category', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING),
            openapi.Parameter('product_factory', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING),
            openapi.Parameter('factory_category', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING),
            openapi.Parameter('created_user', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING),
            openapi.Parameter('salesman', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING),
            openapi.Parameter('client', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING),
        ]
    )
    def get_excel_report(self, request, *args, **kwargs):
        start_date, end_date = self.get_start_end_dates()
        self.request.user = User.objects.get(pk=kwargs['user_id'])
        order_items, order_item_product_factories = self.get_querysets()
        order_items = self.get_filtered_queryset(order_items, self.order_item_filterset_class)
        order_item_product_factories = self.get_filtered_queryset(
            order_item_product_factories,
            self.factory_order_item_filterset_class
        )
        aggregated_data = self.get_aggregated_data(order_items, order_item_product_factories)
        byte_buffer = OrderItemsReportExcelExport(order_items, order_item_product_factories, aggregated_data,
                                                  start_date, end_date).get_excel_file()
        return FileResponse(byte_buffer, filename='Prodazhi_tovarov_otchet.xlsx', as_attachment=True)


# =================== OverallReport =================== #
class OverallReportView(DateTimeRangeFilterMixin, IndustryFilterMixin, APIView):

    def get_order_items(self):
        start_date, end_date = self.get_start_end_dates()
        industries = self.request.query_params.getlist('industry')
        clients = self.request.query_params.getlist('client')
        order_items = OrderItem.objects.filter(
            models.Q(order__created_at__gte=start_date)
            & models.Q(order__created_at__lte=end_date)
            & ~models.Q(order__status=OrderStatus.CANCELLED)
            & models.Q(order__is_deleted=False)
        )

        if industries and industries != []:
            order_items = order_items.filter(product__category__industry__in=industries)

        if clients and clients != []:
            order_items = order_items.filter(models.Q(order__client__in=clients))
        # # if industries:
        # #     qs = qs.by_industries(industries)
        # if self.request.user.type == UserType.MANAGER:
        #     orders = orders.by_user_industry(self.request.user)
        order_items = order_items.with_total_self_price().with_total_profit().with_returned_total_sum()
        return order_items

    def get_order_item_product_factories(self):
        start_date, end_date = self.get_start_end_dates()
        industries = self.request.query_params.getlist('industry')
        clients = self.request.query_params.getlist('client')
        order_items = OrderItemProductFactory.objects.filter(
            models.Q(order__created_at__gte=start_date)
            & models.Q(order__created_at__lte=end_date)
            & ~models.Q(order__status=OrderStatus.CANCELLED)
            & models.Q(order__is_deleted=False)
            & models.Q(is_returned=False)
        )
        if industries and industries != []:
            order_items = order_items.filter(product_factory__category__industry__in=industries)

        if clients and clients != []:
            order_items = order_items.filter(models.Q(order__client__in=clients))

        # # if industries:
        # #     qs = qs.by_industries(industries)
        # if self.request.user.type == UserType.MANAGER:
        #     orders = orders.by_user_industry(self.request.user)
        order_items = order_items.with_total_self_price().with_total_profit().with_returned_total_sum()
        return order_items

    def get_orders(self, order_items, order_item_product_factories):
        orders = Order.objects.filter(
            models.Q(order_items__in=order_items)
            | models.Q(order_item_product_factory_set__in=order_item_product_factories)
        ).distinct().only('debt')
        return orders

    def get_worker_incomes(self):
        start_date, end_date = self.get_start_end_dates()
        return WorkerIncomes.objects.filter(
            models.Q(created_at__gte=start_date)
            & models.Q(created_at__lte=end_date)
        )

    def get_product_write_offs(self):
        start_date, end_date = self.get_start_end_dates()
        industries = self.request.query_params.getlist('industry')

        product_write_offs = WarehouseProductWriteOff.objects.get_available().filter(
            models.Q(created_at__gte=start_date)
            & models.Q(created_at__lte=end_date)
            & models.Q(warehouse_product__product__is_deleted=False)
        )
        if industries and industries != []:
            product_write_offs = product_write_offs.filter(
                warehouse_product__product__category__industry__in=industries)
        return product_write_offs

    def get_factory_write_offs(self):
        start_date, end_date = self.get_start_end_dates()
        industries = self.request.query_params.getlist('industry')

        factory_write_offs = ProductFactory.objects.get_available().filter(
            models.Q(created_at__gte=start_date)
            & models.Q(created_at__lte=end_date)
            & models.Q(status=ProductFactoryStatus.WRITTEN_OFF)
        )
        if industries and industries != []:
            factory_write_offs = factory_write_offs.filter(category__industry__in=industries)
        return factory_write_offs

    def get_payments(self):
        start_date, end_date = self.get_start_end_dates()
        return Payment.objects.get_available().filter(
            models.Q(created_at__gte=start_date)
            & models.Q(created_at__lte=end_date)
            & models.Q(payment_type=PaymentType.OUTCOME)
        )

    @swagger_auto_schema(
        responses={
            200: OverallReportSerializer()
        },
        manual_parameters=[
            openapi.Parameter('start_date', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description="Start date in DD.MM.YYYY format"),
            openapi.Parameter('end_date', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description="End date in DD.MM.YYYY format"),
            openapi.Parameter('industry', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING),
            openapi.Parameter('client', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING),
        ]
    )
    def get(self, request, *args, **kwargs):
        order_items = self.get_order_items()
        order_items_product_factories = self.get_order_item_product_factories()
        orders = self.get_orders(order_items, order_items_product_factories)
        product_write_offs = self.get_product_write_offs()
        factory_write_offs = self.get_factory_write_offs()
        worker_incomes = self.get_worker_incomes()
        payments = self.get_payments()

        order_items_aggs = order_items.aggregate(
            total_sale_sum=Sum(F('total') - F('returned_total_sum'), default=0),
            total_self_price_sum=Sum('total_self_price', default=0),
        )
        order_items_factories_aggs = order_items_product_factories.aggregate(
            total_sale_sum=Sum(F('price') - F('returned_total_sum'), default=0),
            total_self_price_sum=Sum('total_self_price', default=0),
        )

        order_aggs = orders.aggregate(total_debt=Sum(F('debt'), default=0))

        product_write_offs_aggs = product_write_offs.aggregate(
            total_self_price=Sum(F('count') * F('warehouse_product__self_price'), default=0)
        )
        factory_write_offs_aggs = factory_write_offs.aggregate(
            total_self_price=Sum('self_price', default=0)
        )

        worker_incomes_aggs = worker_incomes.aggregate(
            total_sum=Sum(
                models.Case(
                    models.When(income_type=WorkerIncomeType.INCOME, then=F('total')),
                    models.When(income_type=WorkerIncomeType.OUTCOME, then=-F('total')),
                    default=0, output_field=models.DecimalField()
                ),
                default=0
            )
        )

        payments_aggs = payments.aggregate(
            total_sum=Sum('amount', default=0)
        )

        total_sale_sum = order_items_aggs['total_sale_sum'] + order_items_factories_aggs['total_sale_sum']
        total_self_price_sum = order_items_aggs['total_self_price_sum'] \
                               + order_items_factories_aggs['total_self_price_sum']
        total_debt_sum = order_aggs['total_debt']
        total_write_off_sum = product_write_offs_aggs['total_self_price'] + 0
        worker_incomes_sum = worker_incomes_aggs['total_sum']
        outlay_total_sum = payments_aggs['total_sum']
        total_profit_sum = total_sale_sum - total_self_price_sum - outlay_total_sum

        summary_data = {
            "total_sale_sum": total_sale_sum,
            "total_self_price_sum": total_self_price_sum,
            "total_profit_sum": total_profit_sum,
            "total_debt_sum": total_debt_sum,
            "total_write_off_sum": total_write_off_sum,
            "worker_incomes_sum": worker_incomes_sum,
            "outlay_total_sum": outlay_total_sum,
        }

        serializer = OverallReportSerializer(instance=summary_data)
        return Response(data=serializer.data)
