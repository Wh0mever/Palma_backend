import datetime
import os
import textwrap

import django
import requests

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "PalmaCrm.settings"
)

django.setup()

from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.conf import settings
from django.db.models import Sum, F, Q, Subquery, OuterRef, When, Case

from src.core.helpers import my_number_separator
from src.user.enums import WorkerIncomeType
from src.order.enums import OrderStatus
from src.order.models import OrderItem, OrderItemProductFactory, Order, Client
from src.payment.models import Payment, Outlay
from src.payment.enums import PaymentType
from src.user.models import WorkerIncomes
from src.warehouse.models import WarehouseProductWriteOff

User = get_user_model()


def get_summary_data():
    now = timezone.localtime()
    previous_day = now - datetime.timedelta(days=1)
    start_date = datetime.datetime.combine(previous_day.date(), datetime.time.min)
    end_date = datetime.datetime.combine(previous_day.date(), datetime.time.max)

    clients = Client.objects.filter(full_name__icontains='*')

    order_items = OrderItem.objects.filter(
        models.Q(order__created_at__gte=start_date)
        & models.Q(order__created_at__lte=end_date)
        & ~models.Q(order__status=OrderStatus.CANCELLED)
        & models.Q(order__is_deleted=False)
    ).with_total_self_price().with_total_profit().with_returned_total_sum()

    order_items_product_factories = OrderItemProductFactory.objects.filter(
        models.Q(order__created_at__gte=start_date)
        & models.Q(order__created_at__lte=end_date)
        & ~models.Q(order__status=OrderStatus.CANCELLED)
        & models.Q(order__is_deleted=False)
        & models.Q(is_returned=False)
    ).with_total_self_price().with_total_profit().with_returned_total_sum()
    orders = Order.objects.filter(
        models.Q(order_items__in=order_items)
        | models.Q(order_item_product_factory_set__in=order_items_product_factories)
    ).distinct().only('debt')
    # worker_incomes = WorkerIncomes.objects.filter(
    #     models.Q(created_at__gte=start_date)
    #     & models.Q(created_at__lte=end_date)
    # )
    product_write_offs = WarehouseProductWriteOff.objects.get_available().filter(
        models.Q(created_at__gte=start_date)
        & models.Q(created_at__lte=end_date)
        & models.Q(warehouse_product__product__is_deleted=False)
    )
    payments = Payment.objects.get_available().filter(
        models.Q(created_at__gte=start_date)
        & models.Q(created_at__lte=end_date)
        & Q(payment_type=PaymentType.OUTCOME)
    )

    order_items_aggs = order_items.aggregate(
        total_sale_sum=Sum(F('total') - F('returned_total_sum'), default=0),
        total_self_price_sum=Sum('total_self_price', default=0),
        total_shop_sale_sum=Sum(
            F('total') - F('returned_total_sum'),
            default=0,
            filter=~Q(order__client__in=clients) & Q(product__category__industry_id=6)
        ),
        total_clients_sale_sum=Sum(
            F('total') - F('returned_total_sum'),
            default=0,
            filter=Q(order__client__in=clients) & Q(product__category__industry_id=6)
        )
    )
    order_items_factories_aggs = order_items_product_factories.aggregate(
        total_sale_sum=Sum(F('price') - F('returned_total_sum'), default=0),
        total_self_price_sum=Sum('total_self_price', default=0),
        total_shop_sale_sum=Sum(
            F('price') - F('returned_total_sum'),
            default=0,
            filter=~Q(order__client__in=clients) & Q(product_factory__category__industry_id=6)
        ),
        total_clients_sale_sum=Sum(
            F('price') - F('returned_total_sum'),
            default=0,
            filter=Q(order__client__in=clients) & Q(product_factory__category__industry_id=6)
        )
    )

    order_aggs = orders.aggregate(total_debt=Sum(F('debt'), default=0))

    product_write_offs_aggs = product_write_offs.aggregate(
        total_self_price=Sum(F('count') * F('warehouse_product__self_price'), default=0)
    )

    # worker_incomes_aggs = worker_incomes.aggregate(
    #     total_sum=Sum(
    #         models.Case(
    #             models.When(income_type=WorkerIncomeType.INCOME, then=F('total')),
    #             models.When(income_type=WorkerIncomeType.OUTCOME, then=-F('total')),
    #             default=0, output_field=models.DecimalField()
    #         ),
    #         default=0
    #     )
    # )

    # payments_aggs = payments.aggregate(
    #     total_sum=Sum('amount', default=0)
    # )
    # outlays = (
    #     Outlay.objects.filter(payments__in=payments)
    #     .annotate(total_amount=Subquery(
    #         payments.filter(outlay_id=OuterRef('pk'))
    #         .values('outlay_id')
    #         .annotate(total_amount=Sum(
    #             Case(
    #                 When(payment_type=PaymentType.OUTCOME, then=F('-amount')),
    #                 default=F('amount')
    #             ),
    #             default=0
    #         ))
    #         .values('total_amount')[:1]
    #     ))
    # )
    outlays = (
        Outlay.objects.filter(payments__in=payments).distinct()
        .annotate(total_amount=Subquery(
            payments.filter(outlay_id=OuterRef('pk'))
            .values('outlay_id')
            .annotate(total_amount=Sum('amount', default=0))
            .values('total_amount')[:1]
        ))
    )

    total_orders = orders.count()
    total_sale_sum = order_items_aggs['total_sale_sum'] + order_items_factories_aggs['total_sale_sum']
    total_self_price_sum = order_items_aggs['total_self_price_sum'] \
                           + order_items_factories_aggs['total_self_price_sum']
    total_debt_sum = order_aggs['total_debt']
    total_write_off_sum = product_write_offs_aggs['total_self_price'] + 0
    # worker_incomes_sum = worker_incomes_aggs['total_sum']
    outlay_total_sum = outlays.aggregate(total_amount_sum=Sum('total_amount', default=0))['total_amount_sum']
    total_profit_sum = total_sale_sum - total_self_price_sum - outlay_total_sum
    total_factory_shop_sales = order_items_factories_aggs['total_shop_sale_sum'] \
                               + order_items_aggs['total_shop_sale_sum']
    total_factory_clients_sales = order_items_factories_aggs['total_clients_sale_sum'] \
                                  + order_items_aggs['total_clients_sale_sum']

    summary_data = {
        "total_orders": my_number_separator(int(total_orders)),
        "total_sale_sum": my_number_separator(int(total_sale_sum)),
        "total_self_price_sum": my_number_separator(int(total_self_price_sum)),
        "total_profit_sum": my_number_separator(int(total_profit_sum)),
        "total_debt_sum": my_number_separator(int(total_debt_sum)),
        "total_write_off_sum": my_number_separator(int(total_write_off_sum)),
        # "worker_incomes_sum": my_number_separator(int(worker_incomes_sum)),
        "outlay_total_sum": my_number_separator(int(outlay_total_sum)),
        "total_factory_shop_sales": my_number_separator(int(total_factory_shop_sales)),
        "total_factory_clients_sales": my_number_separator(int(total_factory_clients_sales)),
        "outlays": outlays
    }
    return summary_data


def send_daily_report_notification():
    try:
        summary = get_summary_data()
        outlays = summary['outlays']

        outlays_by_category = "\n".join(
            f"{i + 1}) {o.title}: {my_number_separator(o.total_amount)}" for i, o in enumerate(outlays))

        message = textwrap.dedent(f"""\
🎯 <b>Отчет по Продажам</b>

🛒  <i>Кол-во продаж:</i> {summary['total_orders']}
💰  <i>Сумма продаж:</i> {summary['total_sale_sum']} Сум
⚖️  <i>Сумма себестоимости:</i> {summary['total_self_price_sum']} Сум
📈  <i>Сумма прибыли:</i> {summary['total_profit_sum']} Сум
💳  <i>Сумма долга:</i> {summary['total_debt_sum']} Сум
🗑  <i>Сумма списаний:</i> {summary['total_write_off_sum']} Сум
🌸  <i>Сумма продаж цветов (магазин):</i> {summary['total_factory_shop_sales']} Сум
🌼  <i>Сумма продаж цветов (табрик):</i> {summary['total_factory_clients_sales']} Сум

📊 <b>Расходы по Категориям</b>

{outlays_by_category}
💸 <b>Общая сумма расходов:</b> {summary['outlay_total_sum']} Сум
        """)
        chat_ids = [settings.CHAT_ID, settings.SECONDARY_CHAT_ID]
        for chat_id in chat_ids:
            payload = {
                'chat_id': chat_id,
                'text': message,
                'parse_mode': 'Html'
            }
            url = f"{settings.TG_API_URL}{settings.BOT_TOKEN}/sendMessage"
            response = requests.post(url, data=payload)
    except Exception() as e:
        print(e)


def main():
    send_daily_report_notification()


# if __name__ == '__main__':
main()
