from datetime import timedelta
from decimal import Decimal

from django.db import models
from django.db.models import Q, Sum, Case, When, F, ExpressionWrapper, Count, Exists, OuterRef
from django.db.models.functions import TruncDay, Coalesce, Round
from django.utils import timezone
from django.contrib.auth import get_user_model

from src.analytics.enums import ProductAnalyticsIndicator, FloristsAnalyticsIndicator, SalesmenAnalyticsIndicator, \
    OutlaysAnalyticsIndicator
from src.analytics.helpers import get_random_background_color, get_random_border_color, COLORS
from src.factory.enums import ProductFactoryStatus
from src.factory.models import ProductFactoryCategory, ProductFactory, ProductFactoryItem
from src.order.enums import OrderStatus
from src.order.models import OrderItem, OrderItemProductFactory, Order, Client
from src.payment.enums import PaymentModelType, PaymentType, OutlayType
from src.payment.models import Payment, Outlay
from src.product.models import Industry, Product
from src.user.enums import WorkerIncomeReason, WorkerIncomeType, UserType
from src.user.models import WorkerIncomes
from src.warehouse.models import WarehouseProductWriteOff

User = get_user_model()

RESULT_DATE_FORMAT = '%d.%m'
DECIMAL_ROUND = Decimal("0.1")


class IncorrectIndicatorError(Exception):
    pass


class BaseAnalyticsService:
    def __init__(self, start_date, end_date):
        self.start_date = start_date
        self.end_date = end_date

    def get_all_days_list(self):
        delta = self.end_date - self.start_date
        return [
            (self.start_date + timedelta(days=i)).replace(
                hour=0, minute=0, second=0, microsecond=0, tzinfo=timezone.get_current_timezone()
            ) for i in range(delta.days + 1)
        ]

    def filter_by_date_range(self, queryset, date_field='created_at'):
        return queryset.filter(
            Q(**{f'{date_field}__gte': self.start_date}),
            Q(**{f'{date_field}__lte': self.end_date})
        )


class ProfitAnalyticsService(BaseAnalyticsService):

    def get_orders(self):
        orders = Order.objects.get_available().filter(
            Q(status=OrderStatus.COMPLETED),
        ).with_total_with_discount().with_total_discount().with_total_self_price().with_total_profit()
        return self.filter_by_date_range(orders)

    def get_outlay_payments(self):
        payments = Payment.objects.get_available().filter(
            Q(payment_model_type=PaymentModelType.OUTLAY),
        )
        return self.filter_by_date_range(payments)

    def get_worker_incomes(self):
        worker_incomes = WorkerIncomes.objects.filter(
            Q(
                reason__in=[
                    WorkerIncomeReason.PRODUCT_SALE,
                    WorkerIncomeReason.PRODUCT_FACTORY_CREATE,
                    WorkerIncomeReason.PRODUCT_FACTORY_SALE
                ]
            ),
        )
        return self.filter_by_date_range(worker_incomes)

    def get_total_profit_by_day(self, orders, worker_incomes, outlay_payments):
        orders_by_day = (
            orders.annotate(day=TruncDay('created_at'))
            .values('day')
            .annotate(total_profit_sum=Sum('total_profit', default=0))
            .order_by('day')
        )
        # worker_incomes_difference_by_day = (
        #     worker_incomes
        #     .annotate(day=TruncDay('created_at'))
        #     .values('day')
        #     .annotate(
        #         total_difference=Sum(
        #             Case(
        #                 When(income_type=WorkerIncomeType.INCOME, then=F('total')),
        #                 When(income_type=WorkerIncomeType.OUTCOME, then=-F('total')),
        #                 default=0,
        #                 output_field=models.DecimalField()
        #             ), default=0
        #         )
        #     )
        #     .order_by('day')
        # )
        outlays_by_day = (
            outlay_payments.annotate(day=TruncDay('created_at'))
            .values('day')
            .annotate(
                amount_sum=Sum(
                    Case(
                        When(payment_type=PaymentType.OUTCOME, then=F('amount')),
                        When(payment_type=PaymentType.INCOME, then=-F('amount')),
                        default=0, output_field=models.DecimalField()
                    ), default=0
                )
            )
            .order_by('day')
        )

        all_days = self.get_all_days_list()
        result_dict = {day: 0 for day in all_days}

        for entry in orders_by_day:
            result_dict[entry['day']] += entry['total_profit_sum']

        # for entry in worker_incomes_difference_by_day:
        #     result_dict[entry['day']] -= entry['total_difference']

        for entry in outlays_by_day:
            result_dict[entry['day']] -= entry['amount_sum']

        final_totals_list = [
            {'day': day.strftime(RESULT_DATE_FORMAT), 'total': total}
            for day, total in result_dict.items()
        ]
        max_total_profit = max(result['total'] for result in final_totals_list)
        min_total_profit = min(result['total'] for result in final_totals_list)
        return final_totals_list, max_total_profit, min_total_profit

    def get_total_turnover_by_day(self, orders, outlay_payments):
        orders_by_day = (
            orders.annotate(day=TruncDay('created_at'))
            .values('day')
            .annotate(total_with_discount_sum=Sum('total_with_discount', default=0))
            .order_by('day')
        )
        outlays_by_day = (
            outlay_payments.annotate(day=TruncDay('created_at'))
            .values('day')
            .annotate(
                amount_sum=Sum(
                    Case(
                        When(payment_type=PaymentType.INCOME, then=F('amount')),
                        default=0, output_field=models.DecimalField()
                    ), default=0
                )
            )
            .order_by('day')
        )
        all_days = self.get_all_days_list()
        result_dict = {day: 0 for day in all_days}

        for entry in orders_by_day:
            result_dict[entry['day']] += entry['total_with_discount_sum']

        for entry in outlays_by_day:
            result_dict[entry['day']] += entry['amount_sum']

        final_totals_list = [
            {'day': day.strftime(RESULT_DATE_FORMAT), 'total': total}
            for day, total in result_dict.items()
        ]
        max_total_turnover = max(result['total'] for result in final_totals_list)
        min_total_turnover = min(result['total'] for result in final_totals_list)
        return final_totals_list, max_total_turnover, min_total_turnover

    def get_final_result_data(self):
        orders = self.get_orders()
        worker_incomes = self.get_worker_incomes()
        outlays = self.get_outlay_payments()
        total_profit_by_day, max_total_profit, min_total_profit = self.get_total_profit_by_day(
            orders, worker_incomes, outlays
        )
        total_turnover_by_day, max_total_turnover, min_total_turnover = self.get_total_turnover_by_day(orders, outlays)
        return dict(
            labels=[day.strftime(RESULT_DATE_FORMAT) for day in self.get_all_days_list()],
            datasets=[
                dict(
                    label='Оборот',
                    data=[item['total'] for item in total_turnover_by_day],
                    borderColor='rgb(255, 99, 132)',
                    backgroundColor='rgba(255, 99, 132, 0.5)',
                ),
                dict(
                    label='Прибыль',
                    data=[item['total'] for item in total_profit_by_day],
                    borderColor='rgb(53, 162, 235)',
                    backgroundColor='rgba(53, 162, 235, 0.5)',
                ),
            ],
            min=min(min_total_profit, min_total_turnover),
            max=max(max_total_profit, max_total_turnover),
        )


class IndustryProfitAnalyticService(BaseAnalyticsService):
    def __init__(self, start_date, end_date, industry):
        super().__init__(start_date, end_date)
        self.industry = industry

    def get_order_items(self):
        order_items = OrderItem.objects.filter(
            Q(product__category__industry=self.industry) &
            Q(order__status=OrderStatus.COMPLETED) &
            Q(order__is_deleted=False)
        ).with_total_profit().with_returned_total_sum()
        return self.filter_by_date_range(order_items, 'order__created_at')

    def get_factory_order_items(self):
        factory_order_items = OrderItemProductFactory.objects.filter(
            Q(product_factory__category__industry=self.industry) &
            Q(order__status=OrderStatus.COMPLETED) &
            Q(is_returned=False) &
            Q(order__is_deleted=False)
        ).with_total_profit()
        return self.filter_by_date_range(factory_order_items, 'order__created_at')

    def get_outlay_payments(self):
        outlay_payments = Payment.objects.get_available().filter(
            Q(payment_model_type=PaymentModelType.OUTLAY) &
            Q(outlay__industry__isnull=False),
            Q(outlay__industry=self.industry)
        )
        return self.filter_by_date_range(outlay_payments, 'created_at')

    def get_total_turnover_by_day(self, order_items, factory_order_items, outlay_payments):
        order_items_by_day = (
            order_items.annotate(day=TruncDay('order__created_at'))
            .values('day')
            .annotate(total_sum=Sum(F('total') - F('returned_total_sum'), default=0))
            .order_by('day')
        )
        factory_order_items_by_day = (
            factory_order_items.annotate(day=TruncDay('order__created_at'))
            .values('day')
            .annotate(total_sum=Sum('price', default=0))
            .order_by('day')
        )
        outlay_payments_by_day = (
            outlay_payments.annotate(day=TruncDay('created_at'))
            .values('day')
            .annotate(
                amount_sum=Sum(
                    Case(
                        When(payment_type=PaymentType.INCOME, then=F('amount')),
                        default=0, output_field=models.DecimalField()
                    ), default=0
                )
            )
            .order_by('day')
        )

        all_days = self.get_all_days_list()
        result_dict = {day: 0 for day in all_days}

        for entry in order_items_by_day:
            result_dict[entry['day']] += entry['total_sum']
        for entry in factory_order_items_by_day:
            result_dict[entry['day']] += entry['total_sum']
        for entry in outlay_payments_by_day:
            result_dict[entry['day']] += entry['amount_sum']

        final_result_list = [
            {'day': day.strftime(RESULT_DATE_FORMAT), 'total': total}
            for day, total in result_dict.items()
        ]

        max_total_turnover = max(result['total'] for result in final_result_list)
        min_total_turnover = min(result['total'] for result in final_result_list)
        return final_result_list, max_total_turnover, min_total_turnover

    def get_total_profit_by_day(self, order_items, factory_order_items, outlay_payments):
        order_items_by_day = (
            order_items.annotate(day=TruncDay('order__created_at'))
            .values('day')
            .annotate(total_sum=Sum(F('total_profit'), default=0))
            .order_by('day')
        )
        factory_order_items_by_day = (
            factory_order_items.annotate(day=TruncDay('order__created_at'))
            .values('day')
            .annotate(total_sum=Sum('total_profit', default=0))
            .order_by('day')
        )
        outlay_payments_by_day = (
            outlay_payments.annotate(day=TruncDay('created_at'))
            .values('day')
            .annotate(
                amount_sum=Sum(
                    Case(
                        When(payment_type=PaymentType.INCOME, then=-F('amount')),
                        When(payment_type=PaymentType.OUTCOME, then=F('amount')),
                        default=0, output_field=models.DecimalField()
                    ), default=0
                )
            )
            .order_by('day')
        )

        all_days = self.get_all_days_list()
        result_dict = {day: 0 for day in all_days}

        for entry in order_items_by_day:
            result_dict[entry['day']] += entry['total_sum']
        for entry in factory_order_items_by_day:
            result_dict[entry['day']] += entry['total_sum']
        for entry in outlay_payments_by_day:
            result_dict[entry['day']] -= entry['amount_sum']

        final_result_list = [
            {'day': day.strftime(RESULT_DATE_FORMAT), 'total': total}
            for day, total in result_dict.items()
        ]
        max_total_profit = max(result['total'] for result in final_result_list)
        min_total_profit = min(result['total'] for result in final_result_list)
        return final_result_list, max_total_profit, min_total_profit

    def get_final_result_data(self):
        order_items = self.get_order_items()
        factory_order_items = self.get_factory_order_items()
        outlay_payments = self.get_outlay_payments()
        total_profit_by_day, max_total_profit, min_total_profit = self.get_total_profit_by_day(
            order_items, factory_order_items, outlay_payments
        )
        total_turnover_by_day, max_total_turnover, min_total_turnover = self.get_total_turnover_by_day(
            order_items, factory_order_items, outlay_payments
        )
        return dict(
            labels=[day.strftime(RESULT_DATE_FORMAT) for day in self.get_all_days_list()],
            datasets=[
                dict(
                    label='Оборот',
                    data=[item['total'] for item in total_turnover_by_day],
                    borderColor='rgb(255, 99, 132)',
                    backgroundColor='rgba(255, 99, 132, 0.5)',
                ),
                dict(
                    label='Прибыль',
                    data=[item['total'] for item in total_profit_by_day],
                    borderColor='rgb(53, 162, 235)',
                    backgroundColor='rgba(53, 162, 235, 0.5)',
                ),
            ],
            industry_name=self.industry.name if self.industry else None,
            min=min(min_total_profit, min_total_turnover),
            max=max(max_total_profit, max_total_turnover),
        )


class CashierIncomeAnalyticsService(BaseAnalyticsService):
    def get_income_payments(self):
        payments = Payment.objects.get_available().filter(
            payment_type=PaymentType.INCOME,
        )
        return self.filter_by_date_range(payments)

    def get_outcome_payments(self):
        payments = Payment.objects.get_available().filter(
            payment_type=PaymentType.OUTCOME,
        )
        return self.filter_by_date_range(payments)

    def get_cashier_total_income_by_day(self, income_payments):
        income_payments_by_day = (
            income_payments.annotate(day=TruncDay('created_at'))
            .values('day')
            .annotate(total_sum=Sum('amount', default=0))
            .order_by('day')
        )

        all_days = self.get_all_days_list()
        result_dict = {day: 0 for day in all_days}

        for entry in income_payments_by_day:
            result_dict[entry['day']] += entry['total_sum']

        final_result_list = [
            {'day': day.strftime(RESULT_DATE_FORMAT), 'total': total}
            for day, total in result_dict.items()
        ]

        max_total_sum = max(result['total'] for result in final_result_list)
        min_total_sum = min(result['total'] for result in final_result_list)
        return final_result_list, max_total_sum, min_total_sum

    def get_cashier_total_outcome_by_day(self, outcome_payments):
        outcome_payments_by_day = (
            outcome_payments.annotate(day=TruncDay('created_at'))
            .values('day')
            .annotate(total_sum=Sum('amount', default=0))
            .order_by('day')
        )

        all_days = self.get_all_days_list()
        result_dict = {day: 0 for day in all_days}

        for entry in outcome_payments_by_day:
            result_dict[entry['day']] += entry['total_sum']

        final_result_list = [
            {'day': day.strftime(RESULT_DATE_FORMAT), 'total': total}
            for day, total in result_dict.items()
        ]

        max_total_sum = max(result['total'] for result in final_result_list)
        min_total_sum = min(result['total'] for result in final_result_list)
        return final_result_list, max_total_sum, min_total_sum

    def get_final_result_data(self):
        income_payments = self.get_income_payments()
        outcome_payments = self.get_outcome_payments()
        total_income_by_day, max_total_income, min_total_income = self.get_cashier_total_income_by_day(
            income_payments,
        )
        total_outcome_by_day, max_total_outcome, min_total_outcome = self.get_cashier_total_outcome_by_day(
            outcome_payments
        )
        return dict(
            labels=[day.strftime(RESULT_DATE_FORMAT) for day in self.get_all_days_list()],
            datasets=[
                dict(
                    label='Приход',
                    data=[item['total'] for item in total_income_by_day],
                    borderColor='rgb(255, 99, 132)',
                    backgroundColor='rgba(255, 99, 132, 0.5)',
                ),
                dict(
                    label='Расход',
                    data=[item['total'] for item in total_outcome_by_day],
                    borderColor='rgb(53, 162, 235)',
                    backgroundColor='rgba(53, 162, 235, 0.5)',
                ),
            ],
            min=min(min_total_income, min_total_outcome),
            max=max(max_total_income, max_total_outcome),
        )


class IndustrySalesAnalyticsService(BaseAnalyticsService):
    def get_industries(self):
        return Industry.objects.get_available()

    def get_order_items(self):
        order_items = OrderItem.objects.all().with_total_profit().with_returned_total_sum().filter(
            order__is_deleted=False,
            order__status=OrderStatus.COMPLETED
        )
        return self.filter_by_date_range(order_items, 'order__created_at')

    def get_factory_order_items(self):
        factory_order_items = OrderItemProductFactory.objects.filter(
            Q(is_returned=False) &
            Q(order__is_deleted=False) &
            Q(order__status=OrderStatus.COMPLETED)
        ).with_total_profit()
        return self.filter_by_date_range(factory_order_items, 'order__created_at')

    def annotate_total_turnover_sum(self, industries, order_items, factory_order_items):
        industries = industries.annotate(
            total_turnover_sum=Coalesce(
                models.Subquery(
                    order_items.filter(product__category__industry_id=models.OuterRef('pk'))
                    .values('product__category__industry_id')
                    .annotate(total_sum=Sum(F('total') - F('returned_total_sum'), default=0))
                    .values('total_sum')[:1]
                ), models.Value(0), output_field=models.DecimalField()
            ) + Coalesce(
                models.Subquery(
                    factory_order_items.filter(product_factory__category__industry_id=models.OuterRef('pk'))
                    .values('product_factory__category__industry_id')
                    .annotate(total_sum=Sum(F('price'), default=0))
                    .values('total_sum')[:1]
                ), models.Value(0), output_field=models.DecimalField()
            )
        ).exclude(total_turnover_sum=0)

        return industries

    def get_total_turnover_sum_all(self, industries):
        return industries.aggregate(total_sum_all=Sum('total_turnover_sum', default=0))['total_sum_all']

    def annotate_share_percentage(self, industries, total_turnover_sum_all):
        return industries.annotate(
            share_percentage=Round(
                ExpressionWrapper(
                    (F('total_turnover_sum') / total_turnover_sum_all) * 100,
                    output_field=models.FloatField()
                ),
                1
            )
        )

    def annotate_with_colors(self, industries):
        return industries.annotate(
            background=models.Value(get_random_background_color()),
            border=models.Value(get_random_border_color())
        )

    def get_final_result_data(self):
        order_items = self.get_order_items()
        factory_order_items = self.get_factory_order_items()
        industries = self.annotate_total_turnover_sum(self.get_industries(), order_items, factory_order_items)
        industries = self.annotate_share_percentage(industries, self.get_total_turnover_sum_all(industries))
        industries = self.annotate_with_colors(industries)

        result_data_list = []
        for i in range(0, len(industries)):
            result_data_list.append(
                {
                    'name': industries[i].name,
                    'total_turnover_sum': industries[i].total_turnover_sum,
                    'share_percentage': industries[i].share_percentage,
                    'color': COLORS[i],
                }
            )

        return dict(
            labels=[industry.name for industry in industries],
            datasets=[
                {
                    'label': 'Доля из общего оборота',
                    'data': [item['share_percentage'] for item in result_data_list],
                    'borderColor': [item['color'] for item in result_data_list],
                    'backgroundColor': [item['color'] for item in result_data_list],

                }
            ],
        )

    def get_table_data(self):
        order_items = self.get_order_items()
        factory_order_items = self.get_factory_order_items()
        industries = self.annotate_total_turnover_sum(self.get_industries(), order_items, factory_order_items)
        industries = self.annotate_share_percentage(industries, self.get_total_turnover_sum_all(industries))
        industries = self.annotate_with_colors(industries)
        industries = industries.order_by('-share_percentage')

        result_data_list = []
        for i in range(0, len(industries)):
            result_data_list.append(
                {
                    'name': industries[i].name,
                    'total_turnover_sum': industries[i].total_turnover_sum,
                    'share_percentage': industries[i].share_percentage,
                    'color': COLORS[i],
                }
            )
        return result_data_list


class OverallTurnoverShareAnalyticsService(BaseAnalyticsService):

    def get_orders(self):
        orders = (
            Order.objects.get_available()
            .filter(status=OrderStatus.COMPLETED)
            .with_total_with_discount().with_total_self_price().with_total_profit()
        )
        return self.filter_by_date_range(orders)

    def get_worker_incomes(self):
        worker_incomes = WorkerIncomes.objects.filter(
            Q(
                reason__in=[
                    WorkerIncomeReason.PRODUCT_SALE,
                    WorkerIncomeReason.PRODUCT_FACTORY_CREATE,
                    WorkerIncomeReason.PRODUCT_FACTORY_SALE
                ]
            ),
        )
        return self.filter_by_date_range(worker_incomes)

    def get_outlay_payments(self):
        payments = Payment.objects.get_available().filter(
            Q(payment_model_type=PaymentModelType.OUTLAY) &
            ~Q(outlay__outlay_type=OutlayType.WORKERS)
        )
        return self.filter_by_date_range(payments)

    def get_worker_payments(self):
        payments = Payment.objects.get_available().filter(
            payment_model_type=PaymentModelType.OUTLAY,
            outlay__outlay_type=OutlayType.WORKERS
        )
        return self.filter_by_date_range(payments)

    def calculate_total_turnover(self, orders, outlay_payments, worker_payments):
        orders_total = orders.aggregate(total_turnover=models.Sum('total_with_discount', default=0))['total_turnover']
        outlay_payments_total = self.calculate_income_outlay_payments_sum(outlay_payments)
        worker_payments_total = self.calculate_income_outlay_payments_sum(worker_payments)
        return orders_total + outlay_payments_total + worker_payments_total

    def calculate_total_self_price_sum(self, orders):
        total_self_price_sum = orders.aggregate(
            total_self_price_sum=models.Sum('total_self_price', default=0)
        )['total_self_price_sum']
        return total_self_price_sum

    def calculate_total_profit_sum(self, orders, outlay_payments, worker_payments):
        outlay_payments_total_outcome = self.calculate_outcome_outlay_payments_sum(outlay_payments)
        outlay_payments_total_income = self.calculate_income_outlay_payments_sum(outlay_payments)
        worker_payments_total_outcome = self.calculate_outcome_outlay_payments_sum(worker_payments)
        worker_payments_total_income = self.calculate_income_outlay_payments_sum(worker_payments)
        orders_profit_sum = orders.aggregate(
            total_profit_sum=Sum('total_profit', default=0)
        )['total_profit_sum']
        total_profit = orders_profit_sum \
                       - outlay_payments_total_outcome \
                       - worker_payments_total_outcome \
                       + outlay_payments_total_income \
                       + worker_payments_total_income
        return total_profit

    def calculate_total_worker_incomes_sum(self, orders, worker_incomes):
        total_worker_income_sum = worker_incomes.filter(income_type=WorkerIncomeType.INCOME).aggregate(
            total_sum=Sum('total', default=0)
        )['total_sum']
        total_worker_outcome_sum = worker_incomes.filter(income_type=WorkerIncomeType.OUTCOME).aggregate(
            total_sum=Sum('total', default=0)
        )['total_sum']
        total_worker_income_difference = total_worker_income_sum - total_worker_outcome_sum
        return total_worker_income_difference

    def calculate_total_worker_payments_diff(self, worker_payments):
        return worker_payments.aggregate(
            amount_diff=Sum(
                Case(
                    When(payment_type=PaymentType.INCOME, then=F('amount')),
                    When(payment_type=PaymentType.OUTCOME, then=-F('amount')),
                    default=0, output_field=models.DecimalField()
                ), default=0
            )
        )['amount_diff']

    def calculate_income_outlay_payments_sum(self, outlay_payments):
        total_outlay_payments_income = outlay_payments.filter(payment_type=PaymentType.INCOME).aggregate(
            total_sum=Sum('amount', default=0))['total_sum']
        return total_outlay_payments_income

    def calculate_outcome_outlay_payments_sum(self, outlay_payments):
        total_outlay_payments_outcome = outlay_payments.filter(payment_type=PaymentType.OUTCOME).aggregate(
            total_sum=Sum('amount', default=0))['total_sum']
        return total_outlay_payments_outcome

    def calculate_share_percentage(self, total_turnover, total_sum):
        share_percentage = Decimal(total_sum / total_turnover * 100).quantize(DECIMAL_ROUND)
        return share_percentage

    def get_final_result_data(self):
        orders = self.get_orders()
        worker_incomes = self.get_worker_incomes()
        outlay_payments = self.get_outlay_payments()
        worker_payments = self.get_worker_payments()
        total_turnover = self.calculate_total_turnover(orders, outlay_payments, worker_payments)
        total_self_price_sum = self.calculate_total_self_price_sum(orders)
        total_self_price_percentage = self.calculate_share_percentage(total_turnover, total_self_price_sum)
        # total_worker_incomes_sum = self.calculate_total_worker_incomes_sum(
        #     orders, worker_incomes,
        # )
        # total_worker_incomes_percentage = self.calculate_share_percentage(total_turnover, total_worker_incomes_sum)

        total_profit_sum = self.calculate_total_profit_sum(
            orders,
            outlay_payments,
            worker_payments,
        )
        total_profit_percentage = self.calculate_share_percentage(total_turnover, total_profit_sum)

        total_outlay_payments_sum = self.calculate_outcome_outlay_payments_sum(
            outlay_payments,
        )
        total_outlay_payments_percentage = self.calculate_share_percentage(total_turnover, total_outlay_payments_sum)

        total_worker_payments_sum = self.calculate_outcome_outlay_payments_sum(
            worker_payments
        )
        total_worker_payments_percentage = self.calculate_share_percentage(total_turnover, total_worker_payments_sum)

        result_data_list = []
        result_data_list.append(
            {
                'label': 'Себестоимость',
                'total_sum': total_self_price_sum,
                'percentage': total_self_price_percentage,
                'color': COLORS[0],
            }
        )
        result_data_list.append(
            {
                'label': 'Прибыль',
                'total_sum': total_profit_sum,
                'percentage': total_profit_percentage,
                'color': COLORS[1],
            }
        )
        result_data_list.append(
            {
                'label': 'Сотрудники',
                'total_sum': total_worker_payments_sum,
                'percentage': total_worker_payments_percentage,
                'color': COLORS[2],
            }
        )
        result_data_list.append(
            {
                'label': 'Прочие расходы',
                'total_sum': total_outlay_payments_sum,
                'percentage': total_outlay_payments_percentage,
                'color': COLORS[3],
            }
        )
        return result_data_list

    def get_chart_data(self):
        result_data_list = self.get_final_result_data()

        return dict(
            labels=[item['label'] for item in result_data_list],
            datasets=[
                {
                    'label': 'Доля из общего оборота',
                    'data': [item['percentage'] for item in result_data_list],
                    'borderColor': [item['color'] for item in result_data_list],
                    'backgroundColor': [item['color'] for item in result_data_list],

                }
            ],
        )

    def get_table_data(self):
        return self.get_final_result_data()


class ProductAnalyticsService(BaseAnalyticsService):
    def __init__(self, indicator, start_date, end_date):
        super().__init__(start_date, end_date)
        self.indicator = indicator

    def get_products(self):
        products = Product.objects.get_available()
        return products

    def annotate_turnover_sum(self, products):
        products = products.annotate(
            total_turnover=Coalesce(
                models.Subquery(
                    self.filter_by_date_range(OrderItem.objects.all(), 'order__created_at').with_returned_total_sum()
                    .filter(
                        Q(product_id=models.OuterRef('pk')) &
                        Q(order__status=OrderStatus.COMPLETED) &
                        Q(order__is_deleted=False)
                    )
                    .values('product_id')
                    .annotate(total_sum=Sum(F('total') - F('returned_total_sum'), default=0))
                    .values('total_sum')[:1]
                ), models.Value(0), output_field=models.DecimalField()
            )
        )
        return products

    def annotate_turnover_percentage(self, products):
        products = self.annotate_turnover_sum(products)
        total_turnover_sum = products.aggregate(
            total_turnover_sum=Sum('total_turnover', default=0))['total_turnover_sum']
        products = products.annotate(
            turnover_percentage=Round(
                ExpressionWrapper(
                    (F('total_turnover') / total_turnover_sum) * 100,
                    output_field=models.FloatField()
                ), 1
            )
        )
        return products

    def annotate_total_profit_sum(self, products):
        products = products.annotate(
            total_profit=Coalesce(
                models.Subquery(
                    self.filter_by_date_range(OrderItem.objects.all(), 'order__created_at')
                    .filter(
                        Q(product_id=models.OuterRef('pk')) &
                        Q(order__status=OrderStatus.COMPLETED) &
                        Q(order__is_deleted=False)
                    ).with_total_profit()
                    .values('product_id')
                    .annotate(total_profit_sum=Sum(F('total_profit'), default=0))
                    .values('total_profit_sum')[:1]
                ), models.Value(0), output_field=models.DecimalField()
            )
        )
        return products

    def annotate_total_profit_percentage(self, products):
        products = self.annotate_total_profit_sum(products)
        total_profit_sum = products.aggregate(
            total_profit_sum=Sum('total_profit', default=0))['total_profit_sum']
        products = products.annotate(
            profit_percentage=Round(
                ExpressionWrapper(
                    (F('total_profit') / total_profit_sum) * 100,
                    output_field=models.FloatField()
                ), 1
            )
        )
        return products

    def annotate_total_sale_count(self, products):
        products = products.annotate(
            total_sale_count=Coalesce(
                models.Subquery(
                    self.filter_by_date_range(OrderItem.objects.all(), 'order__created_at')
                    .filter(
                        Q(product_id=models.OuterRef('pk')) &
                        Q(order__status=OrderStatus.COMPLETED) &
                        Q(order__is_deleted=False)
                    ).with_returned_count()
                    .values('product_id')
                    .annotate(total_sale_count=Sum(F('count') - F('returned_count'), default=0))
                    .values('total_sale_count')[:1]
                ), models.Value(0), output_field=models.DecimalField()
            )
        )
        return products

    def annotate_write_off_total_sum(self, products):
        products = products.annotate(
            write_off_total_sum=Coalesce(
                Coalesce(
                    models.Subquery(
                        self.filter_by_date_range(WarehouseProductWriteOff.objects.get_available(), 'created_at')
                        .filter(warehouse_product__product_id=models.OuterRef('pk'))
                        .values('warehouse_product__product_id')
                        .annotate(write_off_sum=Sum(F('count') * F('warehouse_product__self_price'), default=0))
                        .values('write_off_sum')[:1]
                    ), models.Value(0), output_field=models.DecimalField()
                ) + Coalesce(
                    models.Subquery(
                        self.filter_by_date_range(
                            ProductFactoryItem.objects.filter(
                                factory__is_deleted=False,
                                factory__status=ProductFactoryStatus.WRITTEN_OFF
                            ),
                            'factory__written_off_at'
                        ).with_returned_self_price_sum()
                        .filter(warehouse_product__product_id=models.OuterRef('pk'))
                        .values('warehouse_product__product_id')
                        .annotate(write_off_sum=Sum(F('total_self_price') - F('returned_self_price_sum'), default=0))
                        .values('write_off_sum')[:1]
                    ), models.Value(0), output_field=models.DecimalField()
                ), models.Value(0), output_field=models.DecimalField()
            )
        )
        return products

    def annotate_write_off_total_count(self, products):
        products = products.annotate(
            write_off_total_count=Coalesce(
                Coalesce(
                    models.Subquery(
                        self.filter_by_date_range(WarehouseProductWriteOff.objects.get_available(), 'created_at')
                        .filter(warehouse_product__product_id=models.OuterRef('pk'))
                        .values('warehouse_product__product_id')
                        .annotate(write_off_count=Sum(F('count'), default=0))
                        .values('write_off_count')[:1]
                    ), models.Value(0), output_field=models.DecimalField()
                ) + Coalesce(
                    models.Subquery(
                        self.filter_by_date_range(
                            ProductFactoryItem.objects.filter(
                                factory__is_deleted=False,
                                factory__status=ProductFactoryStatus.WRITTEN_OFF
                            ),
                            'factory__written_off_at'
                        ).with_returned_count()
                        .filter(warehouse_product__product_id=models.OuterRef('pk'))
                        .values('warehouse_product__product_id')
                        .annotate(write_off_sum=Sum(F('count') - F('returned_count'), default=0))
                        .values('write_off_sum')[:1]
                    ), models.Value(0), output_field=models.DecimalField()
                ), models.Value(0), output_field=models.DecimalField()
            )
        )
        return products

    def get_indicator_method_and_field(self):
        indicator_map = {
            ProductAnalyticsIndicator.TURNOVER_SUM: (self.annotate_turnover_sum, 'total_turnover'),
            ProductAnalyticsIndicator.TURNOVER_PERCENT: (self.annotate_turnover_percentage, 'turnover_percentage'),
            ProductAnalyticsIndicator.PROFIT_SUM: (self.annotate_total_profit_sum, 'total_profit'),
            ProductAnalyticsIndicator.PROFIT_PERCENT: (self.annotate_total_profit_percentage, 'profit_percentage'),
            ProductAnalyticsIndicator.SALE_COUNT: (self.annotate_total_sale_count, 'total_sale_count'),
            ProductAnalyticsIndicator.WRITE_OFF_SUM: (self.annotate_write_off_total_sum, 'write_off_total_sum'),
            ProductAnalyticsIndicator.WRITE_OFF_COUNT: (self.annotate_write_off_total_count, 'write_off_total_count'),
        }

        if self.indicator not in indicator_map:
            raise IncorrectIndicatorError('Invalid indicator')

        return indicator_map[self.indicator]

    def get_final_result_data(self):
        products = self.get_products()
        annotate_method, field_name = self.get_indicator_method_and_field()
        products = annotate_method(products).order_by(f"-{field_name}")[:10]

        return {
            'labels': [product.name for product in products],
            'datasets': [
                {
                    'label': 'Значение',
                    'data': [getattr(product, field_name) for product in products],
                    'borderColor': COLORS[0],
                    'backgroundColor': COLORS[0],
                }
            ],
        }


class ProductFactorySalesAnalyticsService(BaseAnalyticsService):
    def get_product_factory_categories(self):
        return ProductFactoryCategory.objects.get_available()

    def get_product_factories_by_category(self, category_id):
        return ProductFactory.objects.get_available().filter(category_id=category_id)

    def annotate_total_turnover(self, categories):
        return categories.annotate(
            total_turnover=Coalesce(
                models.Subquery(
                    self.filter_by_date_range(OrderItemProductFactory.objects.all(), 'order__created_at')
                    .filter(
                        product_factory__category_id=models.OuterRef('pk'),
                        is_returned=False,
                        product_factory__status=ProductFactoryStatus.SOLD,
                        order__status=OrderStatus.COMPLETED,
                        order__is_deleted=False
                    )
                    .values('product_factory__category_id')
                    .annotate(total_turnover=Sum('price', default=0))
                    .values('total_turnover')[:1]
                ), models.Value(0), output_field=models.DecimalField()
            )
        )

    def annotate_total_self_price(self, categories):
        return categories.annotate(
            total_self_price_sum=Coalesce(
                models.Subquery(
                    self.filter_by_date_range(OrderItemProductFactory.objects.all(), 'order__created_at')
                    .filter(
                        product_factory__category_id=models.OuterRef('pk'),
                        is_returned=False,
                        product_factory__status=ProductFactoryStatus.SOLD,
                        order__status=OrderStatus.COMPLETED,
                        order__is_deleted=False,
                    ).with_total_self_price()
                    .values('product_factory__category_id')
                    .annotate(total_self_price_sum=Sum('total_self_price', default=0))
                    .values('total_self_price_sum')[:1]
                ), models.Value(0), output_field=models.DecimalField()
            )
        )

    def annotate_total_worker_incomes(self, categories):
        return categories.annotate(
            total_worker_incomes_sum=Coalesce(
                models.Subquery(
                    self.filter_by_date_range(WorkerIncomes.objects.all(), 'created_at')
                    .filter(product_factory__category_id=models.OuterRef('pk'))
                    .values('product_factory__category_id')
                    .annotate(
                        total_sum=Sum(
                            Case(
                                When(income_type=WorkerIncomeType.INCOME, then=F('total')),
                                When(income_type=WorkerIncomeType.OUTCOME, then=-F('total')),
                            ), default=0
                        )
                    )
                    .values('total_sum')[:1]
                ), models.Value(0), output_field=models.DecimalField()
            )
        )

    def annotate_total_profit(self, categories):
        categories = self.annotate_total_worker_incomes(categories)
        return categories.annotate(
            total_profit=Coalesce(
                models.Subquery(
                    self.filter_by_date_range(OrderItemProductFactory.objects.all(), 'order__created_at')
                    .filter(
                        product_factory__category_id=models.OuterRef('pk'),
                        is_returned=False,
                        product_factory__status=ProductFactoryStatus.SOLD,
                        order__status__in=[OrderStatus.COMPLETED]
                    ).with_total_self_price()
                    .values('product_factory__category_id')
                    .annotate(
                        total_profit=Sum(
                            F('price') - F('total_self_price'),
                            default=0
                        )
                    )
                    .values('total_profit')[:1]
                ) - F('total_worker_incomes_sum'), models.Value(0), output_field=models.DecimalField()
            )
        )

    def get_annotated_categories(self):
        categories = self.get_product_factory_categories()
        categories = self.annotate_total_turnover(categories)
        categories = self.annotate_total_self_price(categories)
        categories = self.annotate_total_worker_incomes(categories)
        categories = self.annotate_total_profit(categories)
        categories = categories.filter(total_turnover__gt=0)
        return categories

    def get_final_result_data(self):
        categories = self.get_annotated_categories()

        return {
            'labels': [category.name for category in categories],
            'datasets': [
                {
                    'label': 'Прибыль',
                    'data': [category.total_profit for category in categories],
                    'backgroundColor': COLORS[0],
                    # 'stack': 'Stack 0',
                },
                {
                    'label': 'Бонусы сотрудникам',
                    'data': [category.total_worker_incomes_sum for category in categories],
                    'backgroundColor': COLORS[1],
                    # 'stack': 'Stack 0',
                },
                {
                    'label': 'Себестоимость',
                    'data': [category.total_self_price_sum for category in categories],
                    'backgroundColor': COLORS[2],
                    # 'stack': 'Stack 0',
                }
            ],
        }

    def get_table_data(self):
        categories = self.get_annotated_categories()
        return [
            {
                'name': category.name,
                'self_price': {
                    'amount': category.total_self_price_sum,
                    'percentage': Decimal(
                        category.total_self_price_sum / category.total_turnover * 100
                    ).quantize(DECIMAL_ROUND)
                },
                'worker_income': {
                    'amount': category.total_worker_incomes_sum,
                    'percentage': Decimal(
                        category.total_worker_incomes_sum / category.total_turnover * 100
                    ).quantize(DECIMAL_ROUND)
                },
                'profit': {
                    'amount': category.total_profit,
                    'percentage': Decimal(
                        category.total_profit / category.total_turnover * 100
                    ).quantize(DECIMAL_ROUND)
                }
            } for category in categories
        ]


class FloristsAnalyticsService(BaseAnalyticsService):
    def __init__(self, indicator, start_date, end_date):
        super().__init__(start_date, end_date)
        self.indicator = indicator

    def get_florists(self):
        return User.objects.filter(
            is_active=True,
            type__in=[UserType.FLORIST, UserType.FLORIST_PERCENT, UserType.FLORIST_ASSISTANT, UserType.CRAFTER]
        )

    def annotate_finished_products_count(self, florists):
        return florists.annotate(
            finished_products_count=Coalesce(
                models.Subquery(
                    self.filter_by_date_range(ProductFactory.objects.get_available(), 'finished_at')
                    .filter(
                        ~Q(status__in=[ProductFactoryStatus.CREATED, ProductFactoryStatus.PENDING]) &
                        Q(florist_id=models.OuterRef('pk'))
                    )
                    .values('florist_id')
                    .annotate(count_sum=Count('id'))
                    .values('count_sum')[:1]
                ), models.Value(0), output_field=models.DecimalField()
            )
        )

    def annotate_sold_products_count(self, florists):
        return florists.annotate(
            sold_products_count=Coalesce(
                models.Subquery(
                    self.filter_by_date_range(OrderItemProductFactory.objects.all(), 'order__created_at')
                    .filter(
                        Q(order__status=OrderStatus.COMPLETED) &
                        Q(order__is_deleted=False) &
                        Q(is_returned=False) &
                        Q(product_factory__florist_id=models.OuterRef('pk'))
                    )
                    .values('product_factory__florist_id')
                    .annotate(count_sum=Count('id'))
                    .values('count_sum')[:1]
                ), models.Value(0), output_field=models.DecimalField()
            )
        )

    def annotate_sales_amount(self, florists):
        return florists.annotate(
            sales_amount=Coalesce(
                models.Subquery(
                    self.filter_by_date_range(OrderItemProductFactory.objects.all(), 'order__created_at')
                    .filter(
                        Q(order__status=OrderStatus.COMPLETED) &
                        Q(order__is_deleted=False) &
                        Q(is_returned=False) &
                        Q(product_factory__florist_id=models.OuterRef('pk'))
                    )
                    .values('product_factory__florist_id')
                    .annotate(price_sum=Sum('price', default=0))
                    .values('price_sum')[:1]
                ), models.Value(0), output_field=models.DecimalField()
            )
        )

    def annotate_sales_profit_amount(self, florists):
        # TODO: subtract worker incomes
        return florists.annotate(
            sales_profit_amount=Coalesce(
                Coalesce(
                    models.Subquery(
                        self.filter_by_date_range(OrderItemProductFactory.objects.all(), 'order__created_at')
                        .filter(
                            Q(order__status=OrderStatus.COMPLETED) &
                            Q(order__is_deleted=False) &
                            Q(is_returned=False) &
                            Q(product_factory__florist_id=models.OuterRef('pk'))
                        ).with_total_profit()
                        .values('product_factory__florist_id')
                        .annotate(price_sum=Sum('total_profit', default=0))
                        .values('price_sum')[:1]
                    ), models.Value(0), output_field=models.DecimalField()
                ) - Coalesce(
                    models.Subquery(
                        self.filter_by_date_range(WorkerIncomes.objects.all(), 'created_at')
                        .filter(
                            worker_id=models.OuterRef('pk'),
                            reason__in=[
                                WorkerIncomeReason.PRODUCT_FACTORY_SALE,
                                WorkerIncomeReason.PRODUCT_FACTORY_CREATE
                            ]
                        )
                        .values('worker_id')
                        .annotate(
                            total_sum=Sum(
                                Case(
                                    When(income_type=WorkerIncomeType.INCOME, then=F('total')),
                                    When(income_type=WorkerIncomeType.OUTCOME, then=-F('total')),
                                ), default=0
                            )
                        )
                        .values('total_sum')[:1]
                    ), models.Value(0), output_field=models.DecimalField()
                ), models.Value(0), output_field=models.DecimalField()
            )
        )

    def get_indicator_method_and_field(self):
        indicator_map = {
            FloristsAnalyticsIndicator.FINISHED_PRODUCTS: (
                self.annotate_finished_products_count, 'finished_products_count'),
            FloristsAnalyticsIndicator.SOLD_PRODUCTS: (self.annotate_sold_products_count, 'sold_products_count'),
            FloristsAnalyticsIndicator.SALES_AMOUNT: (self.annotate_sales_amount, 'sales_amount'),
            FloristsAnalyticsIndicator.SALES_PROFIT_AMOUNT: (self.annotate_sales_profit_amount, 'sales_profit_amount'),
        }

        if self.indicator not in indicator_map:
            raise IncorrectIndicatorError('Invalid indicator')

        return indicator_map[self.indicator]

    def get_final_result_data(self):
        florists = self.get_florists()
        annotate_method, field_name = self.get_indicator_method_and_field()
        florists = annotate_method(florists).order_by(f"-{field_name}")[:10]

        return {
            'labels': [florist.get_full_name() for florist in florists],
            'datasets': [
                {
                    'fill': 'false',
                    'label': 'Значение',
                    'data': [getattr(florist, field_name) for florist in florists],
                    'borderColor': COLORS[0],
                    'backgroundColor': COLORS[0],
                }
            ],
        }


class SalesmenAnalyticsService(BaseAnalyticsService):
    def __init__(self, indicator, start_date, end_date):
        super().__init__(start_date, end_date)
        self.indicator = indicator

    def get_salesmen(self):
        return User.objects.all().get_workers().filter(orders__isnull=False).distinct()

    def annotate_sales_count(self, salesmen):
        return salesmen.annotate(
            sales_count=Coalesce(
                models.Subquery(
                    self.filter_by_date_range(Order.objects.get_available(), 'created_at')
                    .filter(status=OrderStatus.COMPLETED, salesman_id=models.OuterRef('pk'))
                    .values('salesman_id')
                    .annotate(total_count=Count('id'))
                    .values('total_count')[:1]
                ), models.Value(0), output_field=models.DecimalField()
            )
        )

    def annotate_product_sales_count(self, salesmen):
        return salesmen.annotate(
            product_sales_count=Coalesce(
                Coalesce(
                    models.Subquery(
                        self.filter_by_date_range(OrderItem.objects.all(), 'order__created_at')
                        .filter(
                            order__salesman_id=models.OuterRef('pk'),
                            order__status=OrderStatus.COMPLETED,
                            order__is_deleted=False
                        ).with_returned_count()
                        .values('order__salesman_id')
                        .annotate(count_sum=Sum(F('count') - F('returned_count'), default=0))
                        .values('count_sum')[:1]
                    ), models.Value(0), output_field=models.DecimalField()
                ) + Coalesce(
                    models.Subquery(
                        self.filter_by_date_range(OrderItemProductFactory.objects.all(), 'order__created_at')
                        .filter(
                            order__salesman_id=models.OuterRef('pk'),
                            order__status=OrderStatus.COMPLETED,
                            order__is_deleted=False,
                            is_returned=False
                        )
                        .values('order__salesman_id')
                        .annotate(count_sum=Count('id'))
                        .values('count_sum')[:1]
                    ), models.Value(0), output_field=models.DecimalField()
                ), models.Value(0), output_field=models.DecimalField()
            )
        )

    def annotate_total_sales_sum(self, salesmen):
        return salesmen.annotate(
            sales_amount=Coalesce(
                models.Subquery(
                    self.filter_by_date_range(Order.objects.get_available(), 'created_at')
                    .filter(
                        status=OrderStatus.COMPLETED,
                        salesman_id=models.OuterRef('pk')
                    ).with_total_with_discount()
                    .values('salesman_id')
                    .annotate(total_sum=Sum('total_with_discount', default=0))
                    .values('total_sum')[:1]
                ), models.Value(0), output_field=models.DecimalField()
            )
        )

    def annotate_total_profit_sum(self, salesmen):
        # TODO: subtract worker incomes
        return salesmen.annotate(
            sales_profit_amount=Coalesce(
                models.Subquery(
                    self.filter_by_date_range(Order.objects.get_available(), 'created_at')
                    .filter(
                        status=OrderStatus.COMPLETED,
                        salesman_id=models.OuterRef('pk')
                    ).with_total_profit()
                    .values('salesman_id')
                    .annotate(total_sum=Sum('total_profit', default=0))
                    .values('total_sum')[:1]
                ), models.Value(0), output_field=models.DecimalField()
            )
        )

    def get_indicator_method_and_field(self):
        indicator_map = {
            SalesmenAnalyticsIndicator.SALES_COUNT: (
                self.annotate_sales_count, 'sales_count'),
            SalesmenAnalyticsIndicator.PRODUCT_SALES_COUNT: (self.annotate_product_sales_count, 'product_sales_count'),
            SalesmenAnalyticsIndicator.SALES_AMOUNT: (self.annotate_total_sales_sum, 'sales_amount'),
            SalesmenAnalyticsIndicator.SALES_PROFIT_AMOUNT: (self.annotate_total_profit_sum, 'sales_profit_amount'),
        }

        if self.indicator not in indicator_map:
            raise IncorrectIndicatorError('Invalid indicator')

        return indicator_map[self.indicator]

    def get_final_result_data(self):
        salesmen = self.get_salesmen()
        annotate_method, field_name = self.get_indicator_method_and_field()
        salesmen = annotate_method(salesmen).order_by(f"-{field_name}")[:10]

        return {
            'labels': [salesman.get_full_name() for salesman in salesmen],
            'datasets': [
                {
                    'label': 'Значения',
                    'data': [getattr(salesman, field_name) for salesman in salesmen],
                    'borderColor': COLORS[0],
                    'backgroundColor': COLORS[0],
                }
            ],
        }


class OutlaysAnalyticService(BaseAnalyticsService):
    def __init__(self, indicator, start_date, end_date):
        super().__init__(start_date, end_date)
        self.indicator = indicator

    def get_outlays(self):
        from src.payment.models import Payment

        return Outlay.objects.get_available().annotate(
            has_payments=Exists(Payment.objects.filter(outlay=OuterRef('pk')))
        ).filter(has_payments=True)

    def get_total_payments_amount(self, outlays):
        total_payments_amount = outlays.aggregate(
            total_payments_amount=Sum('payments_amount', default=0)
        )['total_payments_amount']
        return total_payments_amount

    def annotate_income_payments_amount(self, outlays):
        return outlays.annotate(
            payments_amount=Coalesce(
                models.Subquery(
                    self.filter_by_date_range(Payment.objects.get_available())
                    .filter(
                        outlay_id=models.OuterRef('pk'),
                        payment_type=PaymentType.INCOME
                    )
                    .values('outlay_id')
                    .annotate(amount_sum=Sum('amount', default=0))
                    .values('amount_sum')[:1]
                ), models.Value(0), output_field=models.DecimalField()
            )
        ).exclude(payments_amount=0)

    def annotate_outcome_payments_amount(self, outlays):
        return outlays.annotate(
            payments_amount=Coalesce(
                models.Subquery(
                    self.filter_by_date_range(Payment.objects.get_available())
                    .filter(
                        outlay_id=models.OuterRef('pk'),
                        payment_type=PaymentType.OUTCOME
                    )
                    .values('outlay_id')
                    .annotate(amount_sum=Sum('amount', default=0))
                    .values('amount_sum')[:1]
                ), models.Value(0), output_field=models.DecimalField()
            )
        ).exclude(payments_amount=0)

    def annotate_payments_percentage(self, outlays):
        total_payments_amount = self.get_total_payments_amount(outlays)
        outlays = outlays.annotate(
            payments_percentage=Round(
                ExpressionWrapper(
                    (F('payments_amount') / total_payments_amount) * 100,
                    output_field=models.FloatField()
                ), 1
            )
        )
        return outlays

    def get_annotated_outlays(self):
        outlays = self.get_outlays()
        if self.indicator == OutlaysAnalyticsIndicator.OUTCOME:
            outlays = self.annotate_outcome_payments_amount(outlays)
        else:
            outlays = self.annotate_income_payments_amount(outlays)
        outlays = self.annotate_payments_percentage(outlays)
        return outlays

    def get_chart_data(self):
        outlays = self.get_annotated_outlays()

        return {
            'labels': [outlay.title for outlay in outlays],
            'datasets': [
                {
                    'label': "Доля от расходов",
                    'data': [outlay.payments_percentage for outlay in outlays],
                    'borderColor': [COLORS[i] for i in range(0, len(outlays))],
                    'backgroundColor': [COLORS[i] for i in range(0, len(outlays))],
                }
            ],
        }

    def get_table_data(self):
        outlays = self.get_annotated_outlays()
        total_payments_amount = self.get_total_payments_amount(outlays)

        return {
            'total_payments_amount': total_payments_amount,
            'outlays': [
                {
                    'title': outlay.title,
                    'payments_amount': outlay.payments_amount,
                    'payments_percentage': outlay.payments_percentage,
                } for outlay in outlays
            ]
        }


class WriteOffsAnalyticsService(BaseAnalyticsService):
    def get_products(self):
        return Product.objects.get_available()

    def get_total_self_price_sum(self, products):
        return products.aggregate(
            total_self_price_sum=Sum('write_off_self_price_sum', default=0))['total_self_price_sum']

    def annotate_write_off_count(self, products):
        return products.annotate(
            write_off_count=Coalesce(
                Coalesce(
                    models.Subquery(
                        self.filter_by_date_range(WarehouseProductWriteOff.objects.get_available())
                        .filter(warehouse_product__product_id=models.OuterRef('pk'))
                        .values('warehouse_product__product_id')
                        .annotate(count_sum=Sum('count', default=0))
                        .values('count_sum')[:1]
                    ), models.Value(0), output_field=models.DecimalField()
                ) + Coalesce(
                    models.Subquery(
                        self.filter_by_date_range(ProductFactoryItem.objects.all(), 'factory__written_off_at')
                        .filter(
                            warehouse_product__product_id=models.OuterRef('pk'),
                            factory__status=ProductFactoryStatus.WRITTEN_OFF,
                            factory__is_deleted=False
                        ).with_returned_count()
                        .values('warehouse_product__product_id')
                        .annotate(count_sum=Sum(F('count') - F('returned_count'), default=0))
                        .values('count_sum')[:1]
                    ), models.Value(0), output_field=models.DecimalField()
                ), models.Value(0), output_field=models.DecimalField()
            )
        )

    def annotate_write_off_self_price_sum(self, products):
        return products.annotate(
            write_off_self_price_sum=Coalesce(
                Coalesce(
                    models.Subquery(
                        self.filter_by_date_range(WarehouseProductWriteOff.objects.get_available())
                        .filter(warehouse_product__product_id=models.OuterRef('pk'))
                        .values('warehouse_product__product_id')
                        .annotate(self_price_sum=Sum(F('warehouse_product__self_price') * F('count'), default=0))
                        .values('self_price_sum')[:1]
                    ), models.Value(0), output_field=models.DecimalField()
                ) + Coalesce(
                    models.Subquery(
                        self.filter_by_date_range(ProductFactoryItem.objects.all(), 'factory__written_off_at')
                        .filter(
                            warehouse_product__product_id=models.OuterRef('pk'),
                            factory__status=ProductFactoryStatus.WRITTEN_OFF,
                            factory__is_deleted=False
                        ).with_returned_self_price_sum()
                        .values('warehouse_product__product_id')
                        .annotate(self_price_sum=Sum(F('total_self_price') - F('returned_self_price_sum'), default=0))
                        .values('self_price_sum')[:1]
                    ), models.Value(0), output_field=models.DecimalField()
                ), models.Value(0), output_field=models.DecimalField()
            )
        )

    def annotate_write_off_percentage(self, products):
        total_write_off_self_price = self.get_total_self_price_sum(products)
        return products.annotate(
            self_price_sum_percentage=Round(
                ExpressionWrapper(
                    (F('write_off_self_price_sum') / total_write_off_self_price) * 100,
                    output_field=models.FloatField()
                ), 1
            )
        )

    def get_annotated_products(self):
        products = self.get_products()
        products = self.annotate_write_off_count(products)
        products = self.annotate_write_off_self_price_sum(products)
        products = self.annotate_write_off_percentage(products)
        products = products.exclude(write_off_count=0)
        return products

    def get_chart_data(self):
        products = self.get_annotated_products().order_by('-write_off_self_price_sum')[:10]

        return {
            'labels': [product.name for product in products],
            'datasets': [
                {
                    'label': [product.name for product in products],
                    'data': [product.self_price_sum_percentage for product in products],
                    'borderColor': [COLORS[i] for i in range(0, len(products))],
                    'backgroundColor': [COLORS[i] for i in range(0, len(products))],
                }
            ],
        }

    def get_tables_data(self):
        products = self.get_annotated_products()
        products_by_count = products.order_by('-write_off_count')[:10]
        products_by_sum = products.order_by('-write_off_self_price_sum')[:10]
        return {
            "main_table": [
                {
                    'title': product.name,
                    'self_price_sum': product.write_off_self_price_sum,
                    'self_price_percentage': product.self_price_sum_percentage,
                } for product in products_by_sum
            ],
            "count_table": [
                {
                    'title': product.name,
                    'write_off_count': product.write_off_count,
                } for product in products_by_count
            ],
            "sum_table": [
                {
                    'title': product.name,
                    'write_off_count': product.write_off_self_price_sum,
                } for product in products_by_sum
            ]
        }


class ClientsAnalyticsService(BaseAnalyticsService):
    def __init__(self, client_id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client_id = client_id

    def get_clients(self):
        return Client.objects.get_available().filter(id=self.client_id)

    def annotate_total_debt(self, clients):
        return clients.annotate(debt=Coalesce(
            models.Subquery(
                self.filter_by_date_range(Order.objects.get_available())
                .filter(models.Q(client_id=models.OuterRef('pk')) & ~models.Q(status=OrderStatus.CANCELLED))
                .values('client_id')
                .annotate(debt=models.Sum('debt', default=0))
                .values('debt')[:1]
            ), models.Value(0), output_field=models.DecimalField())
        )

    def annotate_orders_count(self, clients):
        return clients.annotate(
            orders_count=Coalesce(
                models.Subquery(
                    self.filter_by_date_range(Order.objects.get_available())
                    .filter(models.Q(client_id=models.OuterRef('pk')) & ~models.Q(status=OrderStatus.CANCELLED))
                    .values('client_id')
                    .annotate(total_count=models.Count('id'))
                    .values('total_count')[:1]
                ), models.Value(0), output_field=models.DecimalField()
            )
        )

    def annotate_orders_sum(self, clients):
        return clients.annotate(
            total_orders_sum=Coalesce(
                models.Subquery(
                    self.filter_by_date_range(Order.objects.get_available())
                    .with_total_with_discount()
                    .filter(models.Q(client_id=models.OuterRef('pk')) & ~models.Q(status=OrderStatus.CANCELLED))
                    .values('client_id')
                    .annotate(total_sum=models.Sum('total_with_discount', default=0))
                    .values('total_sum')[:1]
                ), models.Value(0), output_field=models.DecimalField()
            )
        )

    def annotate_orders_discount_sum(self, clients):
        return clients.annotate(
            total_discount_sum=Coalesce(
                models.Subquery(
                    self.filter_by_date_range(Order.objects.get_available())
                    .with_total_discount()
                    .filter(models.Q(client_id=models.OuterRef('pk')) & ~models.Q(status=OrderStatus.CANCELLED))
                    .values('client_id')
                    .annotate(total_sum=models.Sum('total_discount', default=0))
                    .values('total_sum')[:1]
                ), models.Value(0), output_field=models.DecimalField()
            )
        )

    def get_annotated_clients(self):
        clients = self.get_clients()
        clients = self.annotate_total_debt(clients)
        clients = self.annotate_orders_sum(clients)
        clients = self.annotate_orders_count(clients)
        clients = self.annotate_orders_discount_sum(clients)
        return clients

    def get_chart_data(self, client):
        return {
            'labels': [client.full_name],
            'datasets': [
                {
                    'label': 'Сумма покупок',
                    'data': [client.total_orders_sum],
                    'backgroundColor': COLORS[0],
                    # 'stack': 'Stack 0',
                },
                {
                    'label': 'Долг',
                    'data': [client.debt],
                    'backgroundColor': COLORS[1],
                    # 'stack': 'Stack 0',
                },
                {
                    'label': 'Сумма скидок',
                    'data': [client.total_discount_sum],
                    'backgroundColor': COLORS[2],
                    # 'stack': 'Stack 0',
                }
            ],
        }

    def get_table_data(self, client):
        return {
            "main_table": [
                {
                    'title': "Сумма покупок",
                    'value': client.total_orders_sum,
                },
                {
                    'title': "Долг",
                    'value': client.debt,
                },
                {
                    'title': "Кол-во заказов",
                    'value': client.total_discount_sum,
                }
            ]
        }

    def get_result_data(self):
        client = self.get_annotated_clients().first()
        chart_data = self.get_chart_data(client) if client else None
        table_data = self.get_table_data(client) if client else None
        return {
            'chart': chart_data,
            'table': table_data
        }


class ClientsTopAnalyticsService(BaseAnalyticsService):
    def __init__(self, order_field, client_id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.order_field = order_field if order_field else 'orders_count'
        self.order_field_method_map = {
            'debt': self.annotate_total_debt,
            'total_orders_sum': self.annotate_orders_sum,
            'orders_count': self.annotate_orders_count,
            None: self.annotate_orders_count,
        }
        self.client_id = client_id

    def get_clients(self):
        if self.client_id:
            return Client.objects.get_available().filter(id__in=self.client_id)
        return Client.objects.get_available()

    def annotate_total_debt(self, clients):
        return clients.annotate(aggregated_value=Coalesce(
            models.Subquery(
                self.filter_by_date_range(Order.objects.get_available())
                .filter(models.Q(client_id=models.OuterRef('pk')) & ~models.Q(status=OrderStatus.CANCELLED))
                .values('client_id')
                .annotate(debt=models.Sum('debt', default=0))
                .values('debt')[:1]
            ), models.Value(0), output_field=models.DecimalField())
        )

    def annotate_orders_count(self, clients):
        return clients.annotate(
            aggregated_value=Coalesce(
                models.Subquery(
                    self.filter_by_date_range(Order.objects.get_available())
                    .filter(models.Q(client_id=models.OuterRef('pk')) & ~models.Q(status=OrderStatus.CANCELLED))
                    .values('client_id')
                    .annotate(total_count=models.Count('id'))
                    .values('total_count')[:1]
                ), models.Value(0), output_field=models.DecimalField()
            )
        )

    def annotate_orders_sum(self, clients):
        return clients.annotate(
            aggregated_value=Coalesce(
                models.Subquery(
                    self.filter_by_date_range(Order.objects.get_available())
                    .with_total_with_discount()
                    .filter(models.Q(client_id=models.OuterRef('pk')) & ~models.Q(status=OrderStatus.CANCELLED))
                    .values('client_id')
                    .annotate(total_sum=models.Sum('total_with_discount', default=0))
                    .values('total_sum')[:1]
                ), models.Value(0), output_field=models.DecimalField()
            )
        )

    def annotate_orders_discount_sum(self, clients):
        return clients.annotate(
            aggregated_value=Coalesce(
                models.Subquery(
                    self.filter_by_date_range(Order.objects.get_available())
                    .with_total_discount()
                    .filter(models.Q(client_id=models.OuterRef('pk')) & ~models.Q(status=OrderStatus.CANCELLED))
                    .values('client_id')
                    .annotate(total_sum=models.Sum('total_discount', default=0))
                    .values('total_sum')[:1]
                ), models.Value(0), output_field=models.DecimalField()
            )
        )

    def get_annotated_clients(self):
        clients = self.get_clients()
        clients = self.order_field_method_map[self.order_field](clients)
        if self.order_field:
            clients = clients.order_by(f"-aggregated_value")
        return clients

    def get_final_result_data(self):
        clients = self.get_annotated_clients()[:10]

        return {
            'labels': [client.full_name for client in clients],
            'datasets': [
                {
                    'fill': False,
                    'label': 'Значение',
                    'data': [getattr(client, 'aggregated_value') for client in clients],
                    'borderColor': COLORS[0],
                    'backgroundColor': COLORS[0],
                }
            ],
        }
