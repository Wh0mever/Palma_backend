from django.db import transaction, models
from django.utils.decorators import method_decorator
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from rest_framework import filters
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from src.base.api_views import MultiSerializerViewSetMixin, CustomPagination
from src.base.filter_backends import CustomDateRangeFilter
from src.core.helpers import create_action_notification
from src.income.models import Provider
from src.order.enums import OrderStatus
from src.order.services import update_order_debt
from src.payment.enums import PaymentModelType, PaymentType, PaymentMethods
from src.payment.exceptions import PaymentModelTypeInstanceDoesntExists, PaymentOrderDoesntExists
from src.payment.filters import PaymentFilter
from src.payment.models import Payment, PaymentMethodCategory, PaymentMethod
from src.payment.serializers.payment import PaymentListSerializer, OutlayPaymentCreateSerializer, \
    ProviderPaymentCreateSerializer, IncomePaymentCreateSerializer, OrderPaymentCreateSerializer, \
    PaymentMethodCategorySerializer, PaymentMethodSerializer, PaymentSummaryListSerializer, PaymentUpdateSerializer
from src.payment.services import add_payment_to_provider, delete_payment_from_provider, add_payment_to_order, \
    delete_payment_from_order, add_payment_to_cashier, delete_payment_from_cashier, delete_outlay_payment, \
    delete_provider_payment, delete_income_payment, delete_order_payment, add_payment_to_worker, \
    delete_payment_from_worker
from src.user.enums import UserType


class PaymentDestroyViewMixin:
    def destroy(self, request, *args, **kwargs):
        obj: Payment = self.get_object()
        obj.is_deleted = True
        obj.deleted_user = request.user
        obj.save()
        # create_action_notification(
        #     obj_name=str(obj),
        #     action="Удаление Платежа",
        #     user=request.user.get_full_name(),
        #     details=f"Тип платежа: {obj.get_payment_type_display()}.\n"
        #             f"Причина платежа: {obj.get_payment_model_type_display()}\n"
        #             f"Сумма: {obj.amount}"
        # )
        return Response(status=204)


class PaymentMethodCategoryViewSet(MultiSerializerViewSetMixin, ModelViewSet):
    queryset = PaymentMethodCategory.objects.all()
    serializer_class = PaymentMethodCategorySerializer


class PaymentMethodViewSet(MultiSerializerViewSetMixin, ModelViewSet):
    queryset = PaymentMethod.objects.all()
    serializer_class = PaymentMethodSerializer
    filter_backends = [
        DjangoFilterBackend
    ]
    filterset_fields = ['is_active']


class PaymentViewSet(MultiSerializerViewSetMixin, ModelViewSet):
    queryset = Payment.objects.get_available()
    serializer_action_classes = {
        'list': PaymentListSerializer,
        'get_with_summary_list': PaymentSummaryListSerializer,
        'retrieve': PaymentListSerializer,
    }
    pagination_class = CustomPagination
    filter_backends = [
        CustomDateRangeFilter,
        DjangoFilterBackend,
        filters.SearchFilter
    ]
    filterset_class = PaymentFilter
    filter_date_field = 'created_at',
    search_fields = ('comment',)
    date_filter_ignore_actions = [
        'create', 'partial_update', 'update', 'destroy', 'retrieve'
    ]

    def get_with_summary_list(self, request):
        payments = self.filter_queryset(self.get_queryset())
        total_income = payments.filter(payment_type=PaymentType.INCOME).aggregate(
            amount_sum=models.Sum('amount', default=0))['amount_sum']
        total_outcome = payments.filter(payment_type=PaymentType.OUTCOME).aggregate(
            amount_sum=models.Sum('amount', default=0))['amount_sum']
        total_profit = total_income - total_outcome
        total_count = payments.count()
        summary_data = dict(
            total_income=total_income,
            total_outcome=total_outcome,
            total_profit=total_profit,
            total_count=total_count,
        )

        page = self.paginate_queryset(payments)
        if page is not None:
            serializer = self.get_serializer(instance=dict(
                **summary_data,
                payments=page
            ))
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(instance=dict(
            **summary_data,
            payments=payments
        ))

        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        payment_delete_services = {
            PaymentModelType.OUTLAY: delete_outlay_payment,
            PaymentModelType.PROVIDER: delete_provider_payment,
            PaymentModelType.INCOME: delete_income_payment,
            PaymentModelType.ORDER: delete_order_payment
        }
        instance = self.get_object()
        if not (request.user.is_superuser or request.user.type == UserType.ADMIN):
            raise PermissionDenied
        try:
            delete_service = payment_delete_services.get(instance.payment_model_type)
            delete_service(instance, request.user)
        except KeyError:
            return Response(data={'error': 'Invalid model type'}, status=400)
        except PaymentModelTypeInstanceDoesntExists as e:
            return Response(data={'error': f'{e}'}, status=400)

        return Response(status=204)


@method_decorator(name='create', decorator=swagger_auto_schema(
    request_body=OutlayPaymentCreateSerializer(),
    operation_description="Create payment for specific outlay"
))
class OutlayPaymentViewSet(MultiSerializerViewSetMixin, PaymentDestroyViewMixin, ModelViewSet):
    serializer_action_classes = {
        'list': PaymentListSerializer,
        'create': OutlayPaymentCreateSerializer,
        'update': PaymentUpdateSerializer,
    }
    queryset = Payment.objects.get_available().filter(payment_model_type=PaymentModelType.OUTLAY).prefetch_related(
        'created_user', 'outlay'
    )
    pagination_class = CustomPagination
    filter_backends = [
        CustomDateRangeFilter,
        DjangoFilterBackend,
    ]
    filterset_class = PaymentFilter
    filter_date_field = 'created_at',
    date_filter_ignore_actions = [
        'create', 'partial_update', 'update', 'destroy', 'retrieve'
    ]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        with transaction.atomic():
            # if not self.request.user.has_active_shift():
            #     return Response(data={'error': 'Необходимо открыть смену'}, status=410)
            payment = serializer.save(created_user=self.request.user, payment_model_type=PaymentModelType.OUTLAY)
            add_payment_to_cashier(payment)
            if payment.worker:
                add_payment_to_worker(payment.worker, payment)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=201, headers=headers)

    # def perform_create(self, serializer):
    #     with transaction.atomic():
    #         if self.request.user.has_active_shift():
    #             return Response(data={'error': 'Необходимо открыть смену'}, status=400)
    #         payment = serializer.save(created_user=self.request.user, payment_model_type=PaymentModelType.OUTLAY)
    #         add_payment_to_cashier(payment)
    #         if payment.worker:
    #             add_payment_to_worker(payment.worker, payment)

    def destroy(self, request, *args, **kwargs):
        payment = self.get_object()
        if not (request.user.is_superuser or request.user.type == UserType.ADMIN):
            raise PermissionDenied
        with transaction.atomic():
            delete_payment_from_cashier(payment)
            if payment.worker:
                delete_payment_from_worker(payment.worker, payment)

        return super().destroy(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        payment = self.get_object()
        with transaction.atomic():
            delete_payment_from_cashier(payment)
            if payment.worker:
                delete_payment_from_worker(payment.worker, payment)

            serializer = self.get_serializer(payment, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            payment = serializer.save()
            add_payment_to_cashier(payment)
            if payment.worker:
                add_payment_to_worker(payment.worker, payment)
        return Response(serializer.data)


class ProviderPaymentViewSet(MultiSerializerViewSetMixin, PaymentDestroyViewMixin, ModelViewSet):
    serializer_action_classes = {
        'list': PaymentListSerializer,
        'create': ProviderPaymentCreateSerializer,
        'update': PaymentUpdateSerializer,
    }
    queryset = Payment.objects.get_available().filter(payment_model_type=PaymentModelType.PROVIDER).prefetch_related(
        'created_user', 'provider'
    )
    pagination_class = CustomPagination
    filter_backends = [
        CustomDateRangeFilter,
        DjangoFilterBackend,
    ]
    filterset_class = PaymentFilter
    filter_date_field = 'created_at',
    date_filter_ignore_actions = [
        'create', 'partial_update', 'update', 'destroy', 'retrieve'
    ]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        with transaction.atomic():
            # if not self.request.user.has_active_shift():
            #     return Response(data={'error': 'Необходимо открыть смену'}, status=410)
            serializer.save(created_user=self.request.user, payment_model_type=PaymentModelType.PROVIDER)
            validated_data = serializer.data
            provider = Provider.objects.get(pk=validated_data['item'])
            payment = serializer.instance
            add_payment_to_provider(provider, payment)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=201, headers=headers)

    # def perform_create(self, serializer):
    #     serializer.save(created_user=self.request.user, payment_model_type=PaymentModelType.PROVIDER)
    #     validated_data = serializer.data
    #     provider = Provider.objects.get(pk=validated_data['item'])
    #     payment = serializer.instance
    #     add_payment_to_provider(provider, payment)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if not (request.user.is_superuser or request.user.type == UserType.ADMIN):
            raise PermissionDenied
        delete_payment_from_provider(instance.provider, instance)
        return super().destroy(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        payment = self.get_object()
        with transaction.atomic():
            delete_payment_from_provider(payment.provider, payment)

            serializer = self.get_serializer(payment, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            payment = serializer.save()
            add_payment_to_provider(payment.provider, payment)
        return Response(serializer.data)


class IncomePaymentViewSet(MultiSerializerViewSetMixin, PaymentDestroyViewMixin, ModelViewSet):
    serializer_action_classes = {
        'list': PaymentListSerializer,
        'create': IncomePaymentCreateSerializer,
        'update': PaymentUpdateSerializer,
    }
    queryset = Payment.objects.get_available().filter(payment_model_type=PaymentModelType.INCOME).prefetch_related(
        'created_user', 'income', 'provider'
    )
    pagination_class = CustomPagination
    filter_backends = [
        CustomDateRangeFilter,
        DjangoFilterBackend,
    ]
    filterset_class = PaymentFilter
    filter_date_field = 'created_at',
    date_filter_ignore_actions = [
        'create', 'partial_update', 'update', 'destroy', 'retrieve'
    ]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        with transaction.atomic():
            # if not self.request.user.has_active_shift():
            #     return Response(data={'error': 'Необходимо открыть смену'}, status=410)
            validated_data = serializer.validated_data
            income = validated_data['income']
            serializer.save(
                created_user=self.request.user,
                provider=income.provider,
                payment_model_type=PaymentModelType.INCOME
            )
            add_payment_to_provider(income.provider, serializer.instance)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=201, headers=headers)

    # def perform_create(self, serializer):
    #     validated_data = serializer.validated_data
    #     income = validated_data['income']
    #     serializer.save(
    #         created_user=self.request.user,
    #         provider=income.provider,
    #         payment_model_type=PaymentModelType.INCOME
    #     )
    #     add_payment_to_provider(income.provider, serializer.instance)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if not (request.user.is_superuser or request.user.type == UserType.ADMIN):
            raise PermissionDenied
        delete_payment_from_provider(instance.provider, instance)
        return super().destroy(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        payment = self.get_object()
        with transaction.atomic():
            delete_payment_from_provider(payment.provider, payment)

            serializer = self.get_serializer(payment, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            payment = serializer.save()
            add_payment_to_provider(payment.provider, payment)
        return Response(serializer.data)


class OrderPaymentViewSet(MultiSerializerViewSetMixin, ModelViewSet):
    serializer_action_classes = {
        'list': PaymentListSerializer,
        'create': OrderPaymentCreateSerializer,
        'update': PaymentUpdateSerializer,
    }
    queryset = Payment.objects.get_available().filter(payment_model_type=PaymentModelType.ORDER).prefetch_related(
        'created_user', 'order', 'client'
    )
    pagination_class = CustomPagination
    filter_backends = [
        CustomDateRangeFilter,
        DjangoFilterBackend,
    ]
    filterset_class = PaymentFilter
    filter_date_field = 'created_at',
    date_filter_ignore_actions = [
        'create', 'partial_update', 'update', 'destroy', 'retrieve'
    ]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        with transaction.atomic():
            # if not self.request.user.has_active_shift():
            #     return Response(data={'error': 'Необходимо открыть смену'}, status=410)
            validated_data = serializer.validated_data
            order = validated_data['order']
            serializer.save(
                created_user=self.request.user,
                client=order.client,
                payment_model_type=PaymentModelType.ORDER,
                is_debt=order.status == OrderStatus.COMPLETED
            )
            add_payment_to_order(order, serializer.instance)
            update_order_debt(order.pk)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=201, headers=headers)

    # def perform_create(self, serializer):
    #     validated_data = serializer.validated_data
    #     order = validated_data['order']
    #     serializer.save(
    #         created_user=self.request.user,
    #         client=order.client,
    #         payment_model_type=PaymentModelType.ORDER
    #     )
    #     add_payment_to_order(order, serializer.instance)
    #     update_order_debt(order.pk)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if not (request.user.is_superuser or request.user.type == UserType.ADMIN):
            raise PermissionDenied
        delete_order_payment(instance, request.user)
        return Response(status=204)

    def update(self, request, *args, **kwargs):
        payment = self.get_object()
        with transaction.atomic():
            if not payment.order:
                raise PaymentOrderDoesntExists()
            delete_payment_from_order(payment.order, payment)

            serializer = self.get_serializer(payment, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            payment = serializer.save()
            add_payment_to_order(payment.order, serializer.instance)
            update_order_debt(payment.order_id)
        return Response(serializer.data)


class PaymentCreateOptionsView(APIView):
    def get(self, request):
        return Response(data={
            "payment_types": [{"value": choice[0], "label": choice[1]} for choice in PaymentType.choices],
            "payment_methods": [{"value": choice[0], "label": choice[1]} for choice in PaymentMethods.choices],
            "payment_model_types": [{"value": choice[0], "label": choice[1]} for choice in PaymentModelType.choices],
        }, status=200)


class PaymentModelTypeFilterOptionsView(APIView):
    PAYMENT_MODEL_TYPES = [
        ("OUTLAY", "Расходы"),
        ("ORDER", "Заказ"),
        ("INCOME", "Расход поставщикам"),
    ]

    def get(self, request):
        return Response(data={
            "payment_model_types": [{"value": choice[0], "label": choice[1]} for choice in self.PAYMENT_MODEL_TYPES],
        }, status=200)