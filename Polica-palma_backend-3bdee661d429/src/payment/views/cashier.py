from django.db import models, transaction
from django.db.models import Case, When
from django.utils import timezone
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.generics import RetrieveAPIView, ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from src.base.api_views import MultiSerializerViewSetMixin, CustomPagination
from src.base.filter_backends import CustomDateRangeFilter
from src.core.helpers import create_action_notification
from src.payment.enums import PaymentType
from src.payment.exceptions import DontHaveStartedShifts
from src.payment.models import Cashier, PaymentMethodCategory, CashierShift, Payment
from src.payment.serializers.cashier import CashierSerializer, CashierShiftSerializer, CashierShiftSummaryPageSerializer
from src.payment.services import close_cashier_shift


class CashierListView(ListAPIView):
    queryset = Cashier.objects.all()
    serializer_class = CashierSerializer


class CashierRetrieveView(RetrieveAPIView):
    queryset = Cashier.objects.all()
    serializer_class = CashierSerializer


class CashierDisplayListView(APIView):
    def get(self, reqeust, *args, **kwargs):
        categories = PaymentMethodCategory.objects.all()
        cashiers = []
        for category in categories:
            cashiers_group = Cashier.objects.filter(payment_method__category=category)
            category_sum = cashiers_group.aggregate(amount_sum=models.Sum('amount', default=0))['amount_sum']
            cashiers.append(
                {
                    'name': category.name,
                    'amount': category_sum
                }
            )
        return Response(cashiers)


class CashierShiftViewSet(MultiSerializerViewSetMixin, ModelViewSet):
    queryset = CashierShift.objects.all()
    serializer_action_classes = {
        'list': CashierShiftSerializer,
        'create': CashierShiftSerializer,
        'get_current_shift': CashierShiftSerializer,
        'get_shifts_with_summary': CashierShiftSummaryPageSerializer,
    }
    filter_backends = (
        CustomDateRangeFilter,
    )
    pagination_class = CustomPagination
    filter_date_field = 'start_date',
    date_filter_ignore_actions = []

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        last_shift: CashierShift = CashierShift.objects.filter(end_date__isnull=True, started_user=request.user).first()
        if last_shift:
            return Response(data={"error": "Необходимо закрыть незакрытые смены"}, status=400)
            # last_shift.end_date = timezone.now()
            # last_shift.completed_user = self.request.user
            # last_shift.save()
        serializer.save(started_user=self.request.user)
        # create_action_notification(
        #     obj_name=str(last_shift),
        #     action="Закрытие кассы",
        #     user=self.request.user.get_full_name(),
        #     details=f"Открыл кассу: {last_shift.started_user.get_full_name()}.\n"
        #             f"Закрыл кассу: {last_shift.completed_user.get_full_name()}.\n"
        #             f"Сумма прибыли: {last_shift.get_total_profit()}."
        # )
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=201, headers=headers)

    def close_shift(self, request):
        try:
            with transaction.atomic():
                close_cashier_shift(request.user)
        except DontHaveStartedShifts as e:
            return Response(data={"error": str(e)}, status=400)
        return Response(data={"message": "Смена успешно закрыта"}, status=200)

    def get_current_shift(self, request, *args, **kwargs):
        current_shift = CashierShift.objects.filter(end_date__isnull=True).first()
        serializer = self.get_serializer(instance=current_shift)
        return Response(data=serializer.data)

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('created_user', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING),
        ]
    )
    def get_shifts_with_summary(self, request, *args, **kwargs):
        created_users = request.query_params.getlist('created_user')
        user = request.user
        queryset = self.filter_queryset(self.get_queryset().by_started_user(user))

        if created_users:
            queryset = queryset.filter(started_user__in=created_users)

        aggregated_data = self.get_summary_data(queryset)
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(
                instance=dict(
                    **aggregated_data,
                    shifts=page
                )
            )
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(
            instance=dict(
                **aggregated_data,
                shifts=queryset
            )
        )
        return Response(serializer.data)

    def get_summary_data(self, shifts):
        start_date, end_date = self.request.query_params.get('start_date'), self.request.query_params.get('end_date')
        total_income_sum = shifts.aggregate(
            total_income_sum=models.Sum('overall_income_amount', default=0, output_field=models.DecimalField())
        )['total_income_sum']
        total_outcome_sum = shifts.aggregate(
            total_outcome_sum=models.Sum('overall_outcome_amount', default=0, output_field=models.DecimalField())
        )['total_outcome_sum']
        total_profit_sum = total_income_sum - total_outcome_sum

        # categories = PaymentMethodCategory.objects.all()
        # payments = []
        # for category in categories:
        #     payment_groups = Payment.objects.filter(
        #         payment_method__category=category,
        #         created_at__gte=start_date,
        #         created_at__lte=end_date,
        #     )
        #     category_sum = payment_groups.aggregate(
        #         amount_sum=models.Sum(
        #             Case(
        #                 When(payment_type=PaymentType.INCOME, then=models.F('amount')),
        #                 When(payment_type=PaymentType.OUTCOME, then=-models.F('amount')),
        #                 default=0,
        #                 output_field=models.DecimalField()
        #             ), default=0
        #         ))['amount_sum']
        #     payments.append({
        #         'name': category.name,
        #         'amount': category_sum
        #     })
        return dict(
            total_income_sum=total_income_sum,
            total_outcome_sum=total_outcome_sum,
            total_profit_sum=total_profit_sum,
            # payment_categories=payments
        )
