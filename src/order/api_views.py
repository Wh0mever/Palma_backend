import io
from collections import defaultdict

import pandas as pd
from django.contrib.auth import get_user_model
from django.db import transaction, models
from django.http import Http404, HttpResponse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from rest_framework import filters
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from src.base.api_views import (
    MultiSerializerViewSetMixin,
    DestroyFlagsViewSetMixin, CustomPagination, PermissionPolicyMixin
)
from src.base.filter_backends import CustomDateTimeRangeFilter
from src.core.helpers import send_order_notification, create_order_cancel_notification, \
    create_order_create_notification, get_year_range
from src.factory.enums import ProductFactoryStatus
from src.factory.models import ProductFactory
from src.order.enums import OrderStatus
from src.order.exceptions import NotEnoughProductsInOrderItemError, OrderHasReturnError, RestoreTimeExceedError
from src.order.filters import OrderFilter, ClientFilter
from src.order.models import Client, Order, OrderItem, Department, OrderItemProductReturn, OrderItemProductFactory
from src.order.serializers import (
    ClientSerializer,
    OrderListSerializer,
    OrderDetailSerializer,
    OrderCreateSerializer,
    OrderItemListSerializer,
    OrderItemCreateSerializer,
    OrderItemUpdateSerializer,
    OrderUpdateStatusSerializer,
    DepartmentSerializer,
    OrderCompleteSerializer,
    OrderUpdateSerializer,
    OrderUpdateTotalSerializer,
    OrderItemProductReturnSerializer,
    OrderItemProductReturnCreateSerializer,
    OrderItemProductFactoryUpdateSerializer,
    OrderItemProductFactoryCreateSerializer,
    OrderItemProductFactoryListSerializer, OrderItemProductFactoryReturnListSerializer,
    OrderItemProductFactoryReturnCreateSerializer, OrderListSummarySerializer, ClientWithSummarySerializer
)
from src.order.services import (
    update_order_total,
    update_order_status,
    delete_order,
    create_order_payments_after_complete,
    update_order_debt, return_products_from_order_item_to_warehouse,
    cancel_products_return,
    add_products_to_order,
    handle_order_item_count_change, add_product_factory_to_order, update_order_item_product_factory,
    delete_order_item_product_factory, return_order_item_product_factory, cancel_item_product_factory_return,
    assign_compensation_from_orders_to_workers, handle_order_item_price_change,
    reassign_salesman_compensation_from_order, restore_order, update_client_discount_percent
)
from src.payment.models import PaymentMethod, Payment
from src.product.models import Product
from src.user.enums import UserType
from src.warehouse.exceptions import NotEnoughProductInWarehouseError
from src.warehouse.services import (
    reload_product_from_order_item_to_warehouse
)

User = get_user_model()


class DepartmentViewSet(DestroyFlagsViewSetMixin, ModelViewSet):
    queryset = Department.objects.get_available()
    serializer_class = DepartmentSerializer


class ClientViewSet(MultiSerializerViewSetMixin, DestroyFlagsViewSetMixin, ModelViewSet):
    queryset = Client.objects.get_available().with_debt().with_orders_total_sum().with_orders_count()
    serializer_class = ClientSerializer
    serializer_action_classes = {
        'list': ClientWithSummarySerializer
    }
    filter_backends = [
        filters.SearchFilter,
        DjangoFilterBackend
    ]
    search_fields = ['full_name', 'phone_number']
    filter_class = ClientFilter


class OrderViewSet(MultiSerializerViewSetMixin, PermissionPolicyMixin, ModelViewSet):
    queryset = Order.objects.get_available()
    serializer_class = OrderListSerializer()
    serializer_action_classes = {
        'list': OrderListSerializer,
        'retrieve': OrderDetailSerializer,
        'create': OrderCreateSerializer,
        'partial_update': OrderUpdateSerializer,
        'update_discount': OrderUpdateTotalSerializer,
        'get_summary': OrderListSummarySerializer,
    }
    filter_backends = (
        filters.SearchFilter,
        DjangoFilterBackend,
        CustomDateTimeRangeFilter
    )
    pagination_class = CustomPagination
    filterset_class = OrderFilter
    search_fields = ('client__full_name', 'id')
    filter_date_field = 'created_at',
    date_filter_ignore_actions = [
        'create', 'partial_update', 'update', 'destroy', 'retrieve'
    ]

    permission_classes_per_method = {
        "export_excel": [AllowAny],
    }

    def get_queryset(self):
        qs = super().get_queryset()
        # if not self.request.user.type == UserType.ADMIN:
        #     qs = qs.filter(created_user=self.request.user)
        if self.request.user.type == UserType.MANAGER:
            qs = qs.filter(
                models.Q(order_items__product__category__industry=self.request.user.industry) |
                models.Q(
                    order_item_product_factory_set__product_factory__category__industry=self.request.user.industry) |
                models.Q(created_user__industry=self.request.user.industry)
            ).distinct()
        elif not self.request.user.type in [UserType.ADMIN, UserType.CASHIER]:
            qs = qs.filter(models.Q(salesman=self.request.user) | models.Q(created_user=self.request.user))

        qs = qs.select_related('client', 'department', 'created_user', 'salesman').with_products_discount()

        if self.action in ['retrieve', 'export_excel']:
            qs = qs.prefetch_related(
                models.Prefetch(
                    'order_items',
                    queryset=OrderItem.objects.prefetch_related(
                        'product', 'product__category', 'product__category__industry',
                        models.Prefetch(
                            'product_returns', queryset=OrderItemProductReturn.objects.get_available().select_related(
                                'order_item__product',
                                'created_user',
                                'deleted_user'
                            )
                        )
                    ).with_returned_count().with_returned_total_sum()
                ),
                models.Prefetch(
                    'order_item_product_factory_set',
                    queryset=OrderItemProductFactory.objects.select_related('product_factory')
                ),
                models.Prefetch(
                    'payments',
                    queryset=Payment.objects.get_available()
                )
            )

        if self.action in ['get_summary']:
            qs = (
                qs.with_total_with_discount()
                .with_total_discount()
                .with_total_charge()
                .with_total_self_price()
                .with_total_profit()
                .with_total_debt()
            )
        return qs

    def retrieve(self, request, *args, **kwargs):
        # queryset = self.filter_queryset(self.get_queryset()).filter(
        #     pk=self.kwargs['pk']
        # ).prefetch_related(
        #     models.Prefetch(
        #         'client',
        #         queryset=Client.objects.all().with_orders_count().with_orders_total_sum().with_orders_total_profit()
        #     )
        # )
        instance = self.get_object()
        instance.client = Client.objects.filter(pk=instance.client.pk) \
            .with_debt() \
            .with_orders_count() \
            .with_orders_total_sum() \
            .with_order_total_sum_in_year() \
            .with_orders_count_in_year() \
            .with_orders_total_profit().first()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @swagger_auto_schema(
        request_body=OrderCreateSerializer(),
        responses={
            201: OrderListSerializer(),
        }
    )
    def create(self, request, *args, **kwargs):
        # if not request.user.has_active_shift():
        #     return Response(data={'error': 'Необходимо открыть смену'}, status=410)
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        request_body=OrderUpdateSerializer(),
        responses={
            201: OrderListSerializer(),
        }
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(created_user=self.request.user)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        # if not request.user.has_active_shift():
        #     return Response(data={'error': 'Необходимо открыть смену'}, status=410)
        initial_status = instance.status

        delete_order(instance, self.request.user)
        instance.refresh_from_db()
        if initial_status != OrderStatus.CANCELLED:
            create_order_cancel_notification(instance)
        return Response(status=204)

    def update_discount(self, request, *args, **kwargs):
        order = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        order.discount = data['discount']
        order.save()
        update_order_debt(order.pk)
        order.refresh_from_db(fields=['debt'])
        return Response(data={'message': 'success'})

    def get_summary(self, request, *args, **kwargs):
        orders = self.filter_queryset(self.get_queryset()).filter(~models.Q(status=OrderStatus.CANCELLED))
        aggregated_data = orders.aggregate(
            total_sale_with_discount_amount=models.Sum('total_with_discount', default=0),
            total_discount_amount=models.Sum('total_discount', default=0),
            total_charge_amount=models.Sum('total_charge', default=0),
            total_self_price_amount=models.Sum('total_self_price', default=0),
            total_profit_amount=models.Sum('total_profit', default=0),
            total_debt_amount=models.Sum('debt', default=0),
        )
        summary_data = {
            'total_sale_with_discount_amount': aggregated_data['total_sale_with_discount_amount'],
            'total_discount_amount': aggregated_data['total_discount_amount'],
            'total_charge_amount': aggregated_data['total_charge_amount'],
            'total_self_price_amount': aggregated_data['total_self_price_amount'],
            'total_profit_amount': aggregated_data['total_profit_amount'],
            'total_debt_amount': aggregated_data['total_debt_amount'],
            'created_orders_count': orders.filter(status=OrderStatus.CREATED).count()
        }
        serializer = self.get_serializer(instance=summary_data)
        return Response(serializer.data)

    def export_excel(self, request, *args, **kwargs):
        self.request.user = User.objects.get(pk=kwargs['user_id'])
        salesmen_filter = self.request.query_params.getlist('salesman', None)
        print(salesmen_filter)
        qs = self.get_queryset().order_by('salesman', '-created_at').with_amount_paid() \
            .filter(debt__gt=0, status=OrderStatus.COMPLETED)
        # qs = self.filter_queryset(qs)
        if salesmen_filter:
            qs = qs.filter(salesman__in=salesmen_filter)

        salesman_dict = defaultdict(list)
        for order in qs:
            salesman_name = order.salesman.get_full_name() if order.salesman else 'без продавца'
            salesman_dict[salesman_name].append(order)

        output = io.BytesIO()

        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            for salesman, rows in salesman_dict.items():
                column_names = ['№', 'Заказ', 'Клиент', 'Продавец', 'Создал', 'Сумма', 'Оплачено', 'Долг', 'Дата']
                columns_data = [
                    (
                        i + 1,
                        str(order),
                        order.client.full_name,
                        order.salesman.get_full_name() if order.salesman else "-",
                        order.created_user.get_full_name(),
                        order.get_total_with_discount(),
                        order.amount_paid,
                        order.debt,
                        timezone.localtime(order.created_at).strftime('%d.%m.%Y %H:%M'),
                    ) for i, order in enumerate(rows)
                ]
                df = pd.DataFrame(columns=column_names, data=columns_data)

                start_row = 1
                end_row = start_row + len(df)

                df.to_excel(writer, index=False, sheet_name=f'{salesman[:31]}', startrow=start_row - 1)
                ws = writer.sheets[f'{salesman[:31]}']
                ws.autofit()

                cell_format_props = {
                    'border': 2
                }
                cell_head_format_props = {
                    'border': 2,
                    'bg_color': '#ddebf7',
                    'bold': True,
                }

                cell_format_e = writer.book.add_format(
                    {
                        "align": "center",
                        "font_size": 14,
                        'bold': True
                    }
                )
                # ws.merge_range("A1:G1",
                #                f"Отчет по продажам с долгом от "
                #                f"{timezone.localtime(timezone.now()).strftime('%d.%m.%Y %H:%M')}",
                #                cell_format_e)
                cell_format = writer.book.add_format(
                    cell_format_props
                )
                cell_format_head = writer.book.add_format(
                    cell_head_format_props
                )
                ws.conditional_format(f'A{start_row}:I{end_row}', {
                    'type': 'cell',
                    'criteria': '>=',
                    'value': 0,
                    'format': cell_format,
                })
                ws.conditional_format(f'A{start_row}:I{start_row}', {
                    'type': 'cell',
                    'criteria': '>=',
                    'value': 0,
                    'format': cell_format_head,
                })
                # ws.set_column(0, 0, 5)
                # ws.set_column(1, 3, 20)
                # ws.set_column(4, 4, 40)

        output.seek(0)

        response = HttpResponse(output,
                                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename=s_dolgom.xlsx'
        return response


@method_decorator(name="partial_update", decorator=swagger_auto_schema(
    responses={
        200: OrderItemUpdateSerializer(),
        400: "Error message"
    }
))
class OrderItemViewSet(MultiSerializerViewSetMixin, ModelViewSet):
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemListSerializer
    serializer_action_classes = {
        "create": OrderItemCreateSerializer,
        "partial_update": OrderItemUpdateSerializer
    }

    def get_queryset(self):
        qs = super().get_queryset()
        order_id = self.kwargs.get('order_id')
        qs = qs.filter(order_id=order_id).with_returned_count().with_returned_total_sum()
        qs = qs.prefetch_related(
            'product_returns',
            models.Prefetch('product', Product.objects.with_in_stock()),
        )
        return qs

    @swagger_auto_schema(
        responses={
            201: OrderItemCreateSerializer(),
            400: "Товара 'product_name' недостаточно на складе"
        }
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order_id = self.kwargs.get('order_id')
        order = get_object_or_404(Order, pk=order_id)

        if order.status == OrderStatus.CANCELLED:
            return Response(data={"message": f"Заказ отменен"}, status=400)

        data = serializer.validated_data

        code = data.get('code')
        product = data.get('product')
        count = data['count']

        if not product:
            product = get_object_or_404(Product, code=code)

        try:
            with transaction.atomic():
                # order_item = serializer.save(order=order, price=price, total=total)

                order_item = add_products_to_order(order, product, count)
                update_order_total(order_id)
                update_order_debt(order_id)
                serializer.instance = order_item
        except NotEnoughProductInWarehouseError as e:
            return Response(data={"message": f"{e}"}, status=400)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=201, headers=headers)

    def update(self, request, *args, **kwargs):

        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        order_id = self.kwargs.get('order_id')
        order = get_object_or_404(Order, pk=order_id)
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        order_id = self.kwargs.get('order_id')
        data = serializer.validated_data
        price = data.get('price', instance.price)
        count = data.get('count', instance.count)

        if order.status == OrderStatus.CANCELLED:
            return Response(data={"message": f"Заказ отменен"}, status=400)

        try:
            with transaction.atomic():
                # total = price * count
                handle_order_item_count_change(instance, count)
                handle_order_item_price_change(instance, price)
                # serializer.save(total=total)
                update_order_total(order_id)
                update_order_debt(order_id)
                instance.refresh_from_db()
        except (NotEnoughProductInWarehouseError, NotEnoughProductsInOrderItemError) as e:
            return Response(data={"message": f"{e}"}, status=400)
        # update order and product in instance otherwise they contain old data
        instance.order = Order.objects.get(pk=instance.order_id)
        instance.product = Product.objects.with_in_stock().get(pk=instance.product_id)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance: OrderItem = self.get_object()
        order = instance.order
        product = instance.product
        self.perform_destroy(instance)
        order.refresh_from_db()
        product = Product.objects.with_in_stock().get(pk=product.pk)
        return Response(status=204)

    def perform_destroy(self, instance):
        reload_product_from_order_item_to_warehouse(instance)
        super().perform_destroy(instance)
        update_order_total(instance.order_id)
        update_order_debt(instance.order_id)


class OrderUpdateStatusView(APIView):

    @swagger_auto_schema(
        request_body=OrderUpdateStatusSerializer(),
        responses={200: OrderUpdateStatusSerializer()}
    )
    def post(self, request, *args, **kwargs):
        order_id = kwargs.get('pk')
        order = get_object_or_404(Order, pk=order_id)
        serializer = OrderUpdateStatusSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        status = validated_data.get('status')

        try:
            update_order_status(order, status, request.user)
        except NotEnoughProductInWarehouseError as e:
            return Response(status=400, data={"error": f"{e}"})
        return Response(serializer.data)


class OrderStatusOptionsView(APIView):
    def get(self, request):
        order_status_choices = [{"value": choice[0], "label": choice[1]} for choice in OrderStatus.choices]
        return Response(order_status_choices, status=200)


class OrderCompleteView(APIView):

    @swagger_auto_schema(
        operation_description="Complete order",
        request_body=OrderCompleteSerializer(),
        responses={
            200: OrderDetailSerializer(),
            400: "If the already completed or cancelled or has no order_items",
        },

    )
    def post(self, request, *args, **kwargs):
        order_id = kwargs.get('pk')
        order = get_object_or_404(Order, pk=order_id)

        # if not request.user.has_active_shift():
        #     return Response(data={'error': 'Необходимо открыть смену'}, status=410)
        if order.status == OrderStatus.COMPLETED:
            return Response(data={"error": "Order is already completed"}, status=400)
        if order.status == OrderStatus.CANCELLED:
            return Response(data={"error": "Order is cancelled and can`t be completed"}, status=400)
        if not order.order_items.get_queryset() and not order.order_item_product_factory_set.get_queryset():
            return Response(data={"error": "Order has no order items"}, status=400)

        serializer = OrderCompleteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.data
        payments = validated_data.get('payments')

        with transaction.atomic():
            try:
                if payments:
                    create_order_payments_after_complete(request, order_id, payments)
            except PaymentMethod.DoesNotExist:
                raise Http404
            update_order_status(order, status=OrderStatus.COMPLETED, user=request.user)
            update_order_debt(order_id)
            order.refresh_from_db(fields=['debt', 'status'])
            order.completed_user = request.user
            order.save()
            assign_compensation_from_orders_to_workers(order, order.salesman)
            update_client_discount_percent(order.client)
            create_order_create_notification(order)

        return Response(status=200)


class OrderCancelView(APIView):

    @swagger_auto_schema(
        operation_description="Cancel order",
        responses={200: OrderDetailSerializer()}
    )
    def post(self, request, *args, **kwargs):
        order_id = kwargs.get('pk')
        order = get_object_or_404(Order, pk=order_id)
        # if not request.user.has_active_shift():
        #     return Response(data={'error': 'Необходимо открыть смену'}, status=410)

        if order.status == OrderStatus.CANCELLED:
            return Response(data={"error": "Order is already cancelled"}, status=400)

        has_returns = OrderItemProductReturn.objects.get_available().filter(order=order) \
                      or OrderItemProductFactory.objects.filter(is_returned=True, order=order)
        if has_returns:
            return Response(data={"error": "В заказе есть возвраты"}, status=400)

        update_order_status(order, status=OrderStatus.CANCELLED, user=request.user)

        order.refresh_from_db(fields=['debt'])
        create_order_cancel_notification(order)
        return Response(status=200)


class OrderRestoreView(APIView):
    @swagger_auto_schema(
        operation_description="Restore order",
        responses={200: OrderDetailSerializer()}
    )
    def post(self, request, *args, **kwargs):
        order_id = kwargs.get('pk')
        order = get_object_or_404(Order, pk=order_id)
        if order.status == OrderStatus.CREATED:
            return Response(data={"error": "Заказ уже создан"}, status=400)
        try:
            with transaction.atomic():
                restore_order(order)
        except (NotEnoughProductInWarehouseError, OrderHasReturnError, RestoreTimeExceedError) as e:
            return Response(data={"error": str(e)}, status=400)

        return Response(status=200)


class OrderItemProductReturnViewSet(MultiSerializerViewSetMixin, ModelViewSet):
    queryset = OrderItemProductReturn.objects.filter(is_deleted=False)
    serializer_action_classes = {
        'list': OrderItemProductReturnSerializer,
        'retrieve': OrderItemProductReturnSerializer,
        'create': OrderItemProductReturnCreateSerializer
    }

    def get_queryset(self):
        qs = super().get_queryset()

        order_id = self.kwargs['order_id']
        order_item_id = self.kwargs['order_item_id']
        return qs.filter(order_id=order_id, order_item_id=order_item_id) \
            .select_related('order_item__product', 'created_user', 'deleted_user')

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        order_item = get_object_or_404(OrderItem, pk=self.kwargs['order_item_id'])
        order = order_item.order
        count = data['count']
        total = order_item.price * count

        try:
            with transaction.atomic():
                total_self_price = return_products_from_order_item_to_warehouse(order_item, count)

                instance = serializer.save(
                    order=order,
                    order_item=order_item,
                    total=total,
                    total_self_price=total_self_price,
                    created_user=request.user
                )
                # update_order_item_discount_after_return_created(order_item)
                update_order_total(order_id=order.pk)
                update_order_debt(order_id=order.pk)
                reassign_salesman_compensation_from_order(order_id=order.pk)
                # create_action_notification(
                #     obj_name=str(order_item),
                #     action="Возврат",
                #     user=request.user.get_full_name(),
                #     details=f"Кол-во возвращенных товаров: {count}"
                # )
        except NotEnoughProductsInOrderItemError as e:
            return Response(data={"error": f"{e}"}, status=400)

        return Response(data=OrderItemProductReturnSerializer(instance=instance).data, status=201)

    def destroy(self, request, *args, **kwargs):
        product_return_obj: OrderItemProductReturn = self.get_object()
        order_item = product_return_obj.order_item
        order = product_return_obj.order
        with transaction.atomic():
            try:
                cancel_products_return(order_item, product_return_obj, request.user)
            except NotEnoughProductInWarehouseError as e:
                return Response(data={'error': e}, status=400)
            # update_order_item_discount_after_return_cancelled(order_item)
            update_order_total(order_id=order.pk)
            update_order_debt(order_id=order.pk)
            reassign_salesman_compensation_from_order(order_id=order.pk)
            # create_action_notification(
            #     obj_name=str(order_item),
            #     action="Отмена возврата",
            #     user=request.user.get_full_name(),
            #     details=f"Кол-во отмененных товаров: {product_return_obj.count}"
            # )
        return Response(status=204)


class OrderItemProductFactoryViewSet(MultiSerializerViewSetMixin, ModelViewSet):
    queryset = OrderItemProductFactory.objects.all()
    serializer_action_classes = {
        "list": OrderItemProductFactoryListSerializer,
        "create": OrderItemProductFactoryCreateSerializer,
        "partial_update": OrderItemProductFactoryUpdateSerializer,
        "return_product": OrderItemProductFactoryReturnCreateSerializer,
        "returned_products_list": OrderItemProductFactoryReturnListSerializer,
    }

    def get_order_obj(self):
        order_id = self.kwargs['order_id']
        return get_object_or_404(Order, pk=order_id)

    def get_queryset(self):
        order_id = self.kwargs['order_id']
        qs = super().get_queryset()
        qs = qs.filter(order_id=order_id)
        qs = qs.select_related('order', 'product_factory')
        return qs

    def create(self, request, *args, **kwargs):
        order = self.get_order_obj()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        product_factory = validated_data.get('product_factory')
        code = validated_data.get('code')
        if not product_factory:
            product_factory = get_object_or_404(ProductFactory, product_code=code)

        if product_factory.status != ProductFactoryStatus.FINISHED \
                and not product_factory.is_deleted:
            return Response(data={'error': 'Букет не может быть продан'}, status=400)

        instance = add_product_factory_to_order(order, product_factory)
        order.refresh_from_db()
        serializer.instance = instance
        return Response(serializer.data, 201)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        serializer.instance = update_order_item_product_factory(instance, **validated_data)
        order = serializer.instance.order
        order.refresh_from_db()
        return Response(serializer.data, 200)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        delete_order_item_product_factory(instance)
        order = self.get_order_obj()
        return Response(status=204)

    def returned_products_list(self, request, *args, **kwargs):
        instance = self.get_object()
        queryset = OrderItemProductFactory.objects.filter(pk=instance.pk, is_returned=True)
        serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data)

    def return_product(self, request, *args, **kwargs):
        with transaction.atomic():
            instance: OrderItemProductFactory = self.get_object()
            if instance.is_returned:
                return Response(data={'error': 'Product is already returned'}, status=400)
            return_order_item_product_factory(instance, request.user)
            instance.refresh_from_db()
            reassign_salesman_compensation_from_order(order_id=instance.order_id)
            # create_action_notification(
            #     obj_name=str(instance),
            #     action="Возврат букета",
            #     user=request.user.get_full_name(),
            # )
        return Response(OrderItemProductFactoryListSerializer(instance=instance).data, 200)

    def cancel_return_product(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                instance = self.get_object()
                cancel_item_product_factory_return(instance)

                instance.refresh_from_db()
                reassign_salesman_compensation_from_order(order_id=instance.order_id)
                # create_action_notification(
                #     obj_name=str(instance),
                #     action="Отмена возврата букета",
                #     user=request.user.get_full_name(),
                # )

        except NotEnoughProductInWarehouseError as e:
            return Response(data={"error": str(e)}, status=400)
        return Response(OrderItemProductFactoryListSerializer(instance=instance).data, 200)
