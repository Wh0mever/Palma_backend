import datetime

import requests
from django.conf import settings
from django.db import transaction, models
from django.db.models import Sum, Count, Subquery, OuterRef, Q, DecimalField, Case, When, F
from django.db.models.functions import Coalesce
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from django.contrib.auth import get_user_model
from rest_framework import filters
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from src.base.api_views import MultiSerializerViewSetMixin, CustomPagination
from src.base.filter_backends import CustomDateRangeFilter
from src.core.enums import ActionPermissionRequestType
from src.core.helpers import create_action_notification, try_parsing_date
from src.core.models import ActionPermissionRequest
from src.factory.enums import ProductFactoryStatus, ProductFactorySalesType, FactoryTakeApartRequestType
from src.factory.exceptions import NotEnoughProductInFactoryItemError
from src.factory.filters import ProductFactoryFilter
from src.factory.helpers import generate_product_code
from src.factory.models import (
    ProductFactory,
    ProductFactoryItem,
    ProductFactoryCategory, ProductFactoryItemReturn, FactoryTakeApartRequest
)
from src.factory.serializers import (
    ProductFactorySerializer,
    ProductFactoryDetailSerializer,
    ProductFactoryCreateSerializer,
    ProductFactoryItemDetailSerializer,
    ProductFactoryItemCreateSerializer,
    ProductFactoryItemUpdateSerializer,
    ProductFactoryFinishSerializer,
    ProductFactoryCategorySerializer, ProductFactoryListSerializer, ProductFactoryFinishedListSerializer,
    ProductFactoryItemReturnSerializer, ProductFactoryItemReturnCreateSerializer, ProductFactoryItemWriteOffSerializer,
    ProductFactoryCategoryCreateSerializer, ProductFactoryWrittenOffSummarySerializer, ProductFactorySummarySerializer,
)
from src.factory.services import (
    update_product_factory_self_price,
    delete_product_factory_item,
    create_factory_item,
    update_factory_item, delete_product_factory_category, update_product_factory_total_price,
    assign_product_factory_create_compensation_to_florist, cancel_product_factory_create_compensation_to_florist,
    return_products_from_factory_item, cancel_products_return_from_factory_item, delete_factory_returns,
    write_off_product_from_factory_item, add_charge_to_product_factory, remove_charge_from_product_factory,
    write_off_product_factory, return_to_create
)
from src.order.enums import OrderStatus
from src.order.models import OrderItemProductFactory
from src.user.enums import UserType
from src.warehouse.exceptions import NotEnoughProductInWarehouseError
from src.warehouse.services import reload_product_from_product_factory_to_warehouse

User = get_user_model()


def send_notifications():
    notifications = FactoryTakeApartRequest.objects.filter(is_sent=False).order_by('created_at')
    for notification in notifications:
        message = f"Пользователь: {notification.created_user.first_name}\n" \
                  f"Букет #{notification.product_factory_id}"
        inline_keyboard = [
            [
                {'text': 'Yes', 'callback_data': f'{notification.id}_yes'},
                {'text': 'No', 'callback_data': f'{notification.id}_no'}
            ]
        ]
        payload = {
            'chat_id': settings.CHAT_ID,
            'text': message,
            'reply_markup': {'inline_keyboard': inline_keyboard}
        }
        requests.post(
            url=f'{settings.TG_API_URL}7534609843:AAGan8Q_blDT_c-nNdC34ky0DG0Eiq4Xzqg/sendMessage', json=payload
        )
    notifications.update(is_sent=True)


class ProductFactoryViewSet(MultiSerializerViewSetMixin, ModelViewSet):
    queryset = ProductFactory.objects.get_available()
    serializer_action_classes = {
        'list': ProductFactoryListSerializer,
        'retrieve': ProductFactoryDetailSerializer,
        'create': ProductFactoryCreateSerializer,
        'partial_update': ProductFactoryCreateSerializer,
        'get_summary': ProductFactorySummarySerializer,
        'finish': ProductFactoryFinishSerializer,
        'finished_list': ProductFactoryFinishedListSerializer,
        'written_off_list': ProductFactoryListSerializer,
        'written_off_summary': ProductFactoryWrittenOffSummarySerializer,
        'get_by_florist': ProductFactoryListSerializer,
        'get_for_sale_list': ProductFactoryListSerializer,
    }

    filter_backends = [
        DjangoFilterBackend,
        CustomDateRangeFilter,
        filters.SearchFilter
    ]
    pagination_class = CustomPagination

    search_fields = ['name', 'category__name']
    filterset_class = ProductFactoryFilter
    filter_date_field = 'created_at',
    date_filter_ignore_actions = [
        'create', 'partial_update', 'get_for_sale_list', 'request_write_off',
        'update', 'write_off', 'finish', 'return_to_create', 'request_return_to_create', 'destroy', 'retrieve'
    ]

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.select_related('created_user', 'finished_user', 'deleted_user', 'category__industry', 'florist')

        if self.action in ['retrieve']:
            qs = qs.prefetch_related(
                models.Prefetch(
                    'product_factory_item_set',
                    ProductFactoryItem.objects
                    .select_related('warehouse_product__product__category__industry')
                    .prefetch_related(models.Prefetch(
                        'product_returns', ProductFactoryItemReturn.objects.get_available()
                    ))
                )
            )
        if self.action not in ['get_for_sale_list'] \
                and self.request.user.type not in [UserType.SALESMAN, UserType.CASHIER]:
            qs = qs.by_user_industry(self.request.user)
        return qs

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        florist = validated_data.get('florist')
        if self.request.user.type == UserType.CRAFTER:
            instance = serializer.save(created_user=request.user, florist=request.user)
            instance.name = f"Букет #{instance.pk}"
        else:
            if not florist:
                raise ValidationError('florist is required field')
            else:
                instance = serializer.save(created_user=request.user)
                instance.name = f"Букет #{instance.pk}"

        produce_code = generate_product_code(instance)
        instance.product_code = produce_code
        instance.save()

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=201, headers=headers)

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.status == ProductFactoryStatus.PENDING:
            return Response({'error': 'Букет находится в ожидании разборки'}, status=400)
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        new_florist = serializer.validated_data.get('florist')
        if new_florist and new_florist != instance.florist:
            if not request.user.type == UserType.ADMIN:
                return Response({'error': 'У вас нет доступа на изменение флориста'}, status=400)

        serializer.save()

        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        with transaction.atomic():
            instance = self.get_object()

            if instance.status == ProductFactoryStatus.PENDING:
                return Response({'error': 'Букет находится в ожидании разборки'}, status=400)

            reload_product_from_product_factory_to_warehouse(instance.pk)
            delete_factory_returns(instance.pk, request.user)

            if instance.status == ProductFactoryStatus.FINISHED:
                cancel_product_factory_create_compensation_to_florist(instance)
            instance.is_deleted = True
            instance.deleted_user = request.user
            instance.save()
            # create_action_notification(
            #     obj_name=str(instance),
            #     action="Удаление букета",
            #     user=request.user.get_full_name(),
            #     details=f"Флорист: {instance.florist.get_full_name()}\n"
            #             f"Цена: {instance.price} сум\n"
            #             f"Себестоимость: {instance.self_price}"
            # )
        return Response(status=204)

    def get_summary(self, request):
        qs = self.filter_queryset(self.get_queryset())
        qs = qs.annotate(
            order_sale_price=Coalesce(
                Subquery(
                    OrderItemProductFactory.objects.filter(
                        Q(product_factory_id=OuterRef('pk'))
                        & ~Q(order__status=OrderStatus.CANCELLED)
                        & Q(is_returned=False)
                    )
                    .values('product_factory_id')
                    .annotate(amount_sum=Sum('price', default=0))
                    .values('amount_sum')[:1]
                ), 0, output_field=DecimalField()
            )
        )
        aggregated_data = qs.aggregate(
            total_sale_price_sum=Sum(
                Case(When(status=ProductFactoryStatus.SOLD, then=F('order_sale_price')), default=F('price')),
                default=0
            ),
            total_self_price_sum=Sum('self_price', default=0),
            total_count=Count('id'),
        )
        data = dict(
            **aggregated_data,
            total_profit_sum=aggregated_data['total_sale_price_sum'] - aggregated_data['total_self_price_sum']
        )
        serializer = self.get_serializer(data)
        return Response(serializer.data)

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('start_date', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description="Start date in DD.MM.YYYY format"),
            openapi.Parameter('end_date', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description="End date in DD.MM.YYYY format"),
        ]
    )
    def finished_list(self, request, *args, **kwargs):
        qs = self.filter_queryset(self.get_queryset())
        qs = qs.filter(status=ProductFactoryStatus.FINISHED)
        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data, status=200)

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('start_date', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description="Start date in DD.MM.YYYY format"),
            openapi.Parameter('end_date', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description="End date in DD.MM.YYYY format"),
        ]
    )
    def written_off_list(self, request, *args, **kwargs):
        # search = request.query_params.get('search')
        # start_date = request.query_params.get('start_date',
        #                                       datetime.datetime.today().replace(hour=0, minute=0, second=0))
        # end_date = request.query_params.get('end_date', datetime.datetime.now())
        # if isinstance(start_date, str):
        #     start_date = try_parsing_date(start_date)
        # if isinstance(end_date, str):
        #     end_date = try_parsing_date(end_date)
        self.filter_date_field = 'written_off_at',
        qs = self.get_queryset()
        qs = qs.filter(
            status=ProductFactoryStatus.WRITTEN_OFF,
            # written_off_at__range=[start_date, end_date]
        ).order_by('-written_off_at')

        # if search:
        #     qs = qs.filter(
        #         name__icontains=search,
        #         category__name__icontains=search,
        #     )

        qs = self.filter_queryset(qs)
        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data, status=200)

    def written_off_summary(self, request):
        qs = self.get_queryset()
        self.filter_date_field = 'written_off_at',
        qs = qs.filter(
            status=ProductFactoryStatus.WRITTEN_OFF,
        ).order_by('-written_off_at')

        qs = self.filter_queryset(qs)

        data = qs.aggregate(
            total_self_price=Sum('self_price', default=0),
            total_count=Count('id'),
        )
        serializer = self.get_serializer(instance=data)
        return Response(serializer.data)

    def get_by_florist(self, request, *args, **kwargs):
        florist_id = kwargs.get('florist_id')
        florist = get_object_or_404(User, pk=florist_id)
        qs = self.get_queryset()
        qs.filter(florist=florist)
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data, status=200)

    def finish(self, request, *args, **kwargs):
        with transaction.atomic():
            instance: ProductFactory = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)

            if instance.status == ProductFactoryStatus.PENDING:
                return Response({'error': 'Букет находится в ожидании разборки'}, status=400)

            if not instance.product_factory_item_set:
                return Response(data={"error": "Букет должен состоять минимум из одного материала"}, status=400)

            finished_at = timezone.now()
            serializer.save(status=ProductFactoryStatus.FINISHED, finished_user=request.user, finished_at=finished_at)
            assign_product_factory_create_compensation_to_florist(serializer.instance)
            add_charge_to_product_factory(instance)
        return Response(data={"status": instance.status}, status=200)

    def write_off(self, request, *args, **kwargs):
        with transaction.atomic():
            instance: ProductFactory = self.get_object()
            is_succeed, message = write_off_product_factory(instance)
            if not is_succeed:
                return Response(data={'error': message})
        return Response(data={"status": instance.status}, status=200)

    def request_write_off(self, request, *args, **kwargs):
        with transaction.atomic():
            instance = self.get_object()
            if instance.status == ProductFactoryStatus.SOLD:
                return Response(data={'error': "Нельзя списать проданный товар"})
            if instance.status == ProductFactoryStatus.PENDING:
                return Response(data={'error': "Букет находится в ожидании"})

            if not FactoryTakeApartRequest.objects.filter(product_factory=instance, is_answered=False).exists():
                FactoryTakeApartRequest.objects.create(
                    created_user=request.user,
                    product_factory=instance,
                    request_type=FactoryTakeApartRequestType.WRITE_OFF,
                    initial_status=instance.status
                )

            instance.status = ProductFactoryStatus.PENDING
            instance.save()
            # send_notifications()
        return Response(data={"status": instance.status}, status=200)

    def request_return_to_create(self, request, *args, **kwargs):
        with transaction.atomic():
            instance = self.get_object()
            if instance.status != ProductFactoryStatus.FINISHED:
                return Response(data={"error": "Букет должен быть завершен"}, status=400)
            if instance.status == ProductFactoryStatus.PENDING:
                return Response(data={'error': "Букет находится в ожидании"})

            if not FactoryTakeApartRequest.objects.filter(product_factory=instance, is_answered=False).exists():
                FactoryTakeApartRequest.objects.create(
                    created_user=request.user,
                    product_factory=instance,
                    request_type=FactoryTakeApartRequestType.TO_CREATE,
                    initial_status=instance.status
                )

            instance.status = ProductFactoryStatus.PENDING
            instance.save()
            # send_notifications()
        return Response(data={"status": instance.status}, status=200)

    def return_to_create(self, request, *args, **kwargs):
        with transaction.atomic():
            instance = self.get_object()

            is_succeed, message = return_to_create(instance)
            if not is_succeed:
                return Response(data={'error': message})
        return Response(data={"status": instance.status}, status=200)

    def get_for_sale_list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        queryset = queryset.filter(status=ProductFactoryStatus.FINISHED)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class ProductFactoryItemViewSet(MultiSerializerViewSetMixin, ModelViewSet):
    queryset = ProductFactoryItem.objects.all()
    serializer_action_classes = {
        'list': ProductFactoryItemDetailSerializer,
        'retrieve': ProductFactoryItemDetailSerializer,
        'create': ProductFactoryItemCreateSerializer,
        'partial_update': ProductFactoryItemUpdateSerializer,
        'write_off_product': ProductFactoryItemWriteOffSerializer,
    }

    def get_product_factory_obj(self):
        return get_object_or_404(ProductFactory, pk=self.kwargs.get('product_factory_id'))

    def get_queryset(self):
        qs = super().get_queryset()

        product_factory = self.get_product_factory_obj()
        qs = qs.filter(factory=product_factory)
        qs = qs.select_related('factory', 'warehouse_product__product__category__industry')
        qs = qs.prefetch_related(
            models.Prefetch('product_returns', queryset=ProductFactoryItemReturn.objects.get_available())
        )

        return qs

    def create(self, request, *args, **kwargs):
        product_factory = self.get_product_factory_obj()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        if product_factory.status == ProductFactoryStatus.PENDING:
            return Response({'error': 'Букет находится в ожидании разборки'}, status=400)
        try:
            with transaction.atomic():
                instance = create_factory_item(product_factory, **data)
                serializer.instance = instance
                update_product_factory_self_price(product_factory.pk)
                update_product_factory_total_price(product_factory.pk)
        except NotEnoughProductInWarehouseError as e:
            return Response(data={'error': str(e)}, status=400)
        return Response(data=serializer.data, status=201)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        product_factory = self.get_product_factory_obj()
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        if product_factory.status == ProductFactoryStatus.PENDING:
            return Response({'error': 'Букет находится в ожидании разборки'}, status=400)

        try:
            with transaction.atomic():
                update_factory_item(instance, **validated_data)
                update_product_factory_self_price(product_factory.pk)
                update_product_factory_total_price(product_factory.pk)
        except (NotEnoughProductInWarehouseError, NotEnoughProductInFactoryItemError) as e:
            return Response(data={'error': str(e)}, status=400)
        return Response(serializer.data, status=200)

    def destroy(self, request, *args, **kwargs):
        instance: ProductFactoryItem = self.get_object()
        if instance.factory.status == ProductFactoryStatus.PENDING:
            return Response({'error': 'Букет находится в ожидании разборки'}, status=400)
        delete_product_factory_item(instance)
        update_product_factory_self_price(instance.factory_id)
        update_product_factory_total_price(instance.factory_id)
        return Response(status=204)

    def write_off_product(self, request, *args, **kwargs):
        instance: ProductFactoryItem = self.get_object()
        serializer = self.get_serializer(instance=instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        write_off_count = validated_data['write_off_count']
        if instance.factory.status == ProductFactoryStatus.PENDING:
            return Response({'error': 'Букет находится в ожидании разборки'}, status=400)
        with transaction.atomic():
            try:
                write_off_obj = write_off_product_from_factory_item(instance, write_off_count, request.user)
                update_product_factory_self_price(instance.factory_id)
                update_product_factory_total_price(instance.factory_id)
            except NotEnoughProductInFactoryItemError:
                return Response({'error': 'Недостаточно товаров для списания'}, status=400)

            ActionPermissionRequest.objects.create(
                created_user=request.user,
                wh_product_write_off=write_off_obj,
                request_type=ActionPermissionRequestType.PRODUCT_WRITE_OFF,
            )
        return Response(data={'message': 'Товар успешно списан'})


class ProductFactoryCategoryViewSet(MultiSerializerViewSetMixin, ModelViewSet):
    queryset = ProductFactoryCategory.objects.get_available()
    serializer_class = ProductFactoryCategorySerializer
    serializer_action_classes = {
        'create': ProductFactoryCategoryCreateSerializer,
        'partial_update': ProductFactoryCategoryCreateSerializer,
    }

    # def get_queryset(self):
    #     qs = super().get_queryset()
    #     qs = qs.by_user_industry(self.request.user)
    #     return qs

    def perform_destroy(self, instance):
        delete_product_factory_category(instance)


class ProductFactoryItemReturnViewSet(MultiSerializerViewSetMixin, ModelViewSet):
    queryset = ProductFactoryItemReturn.objects.get_available()
    serializer_class = ProductFactoryItemReturnSerializer
    serializer_action_classes = {
        'create': ProductFactoryItemReturnCreateSerializer
    }

    def get_product_factory_item(self):
        product_factory_item_id = self.kwargs.get('item_id')
        product_factory_item = get_object_or_404(ProductFactoryItem, pk=product_factory_item_id)
        return product_factory_item

    def get_queryset(self):
        qs = super().get_queryset()
        factory_item_id = self.kwargs.get('item_id')
        qs = qs.filter(factory_item_id=factory_item_id).select_related('created_user', 'deleted_user', 'factory_item')
        return qs

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        try:
            with transaction.atomic():
                product_factory_item = self.get_product_factory_item()
                count = data.get('count')
                return_products_from_factory_item(product_factory_item, count)

                total_self_price = product_factory_item.warehouse_product.self_price * count
                total_price = product_factory_item.price * count
                serializer.save(
                    factory_item=product_factory_item,
                    total_self_price=total_self_price,
                    total_price=total_price,
                    created_user=self.request.user
                )
                update_product_factory_self_price(product_factory_item.factory_id)
                update_product_factory_total_price(product_factory_item.factory_id)
        except NotEnoughProductInFactoryItemError:
            return Response(data={"error": "Недостаточно товаров для возврата"}, status=400)

        return Response(serializer.data, status=201)

    def destroy(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                instance: ProductFactoryItemReturn = self.get_object()
                factory_item = instance.factory_item

                cancel_products_return_from_factory_item(instance, request.user)

                update_product_factory_self_price(factory_item.factory_id)
                update_product_factory_total_price(factory_item.factory_id)
                return Response(status=204)
        except NotEnoughProductInWarehouseError as e:
            return Response(data={'error': str(e)}, status=400)


class ProductFactoryStatusOptionsView(APIView):
    def get(self, request):
        product_factory_status_choices = [
            {"value": choice[0], "label": choice[1]} for choice in ProductFactoryStatus.choices
        ]
        return Response(product_factory_status_choices, status=200)


class ProductFactorySalesTypeOptionsView(APIView):
    def get(self, request):
        product_factory_sales_type_choices = [
            {"value": choice[0], "label": choice[1]} for choice in ProductFactorySalesType.choices
        ]
        if not self.request.user.is_anonymous and self.request.user.type == UserType.CRAFTER:
            product_factory_sales_type_choices = [
                d for d in product_factory_sales_type_choices if d['value'] != ProductFactorySalesType.SHOWCASE
            ]
        return Response(product_factory_sales_type_choices, status=200)
