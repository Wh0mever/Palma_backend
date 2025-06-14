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

from django.db.models.functions import Coalesce
from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.conf import settings
from django.db.models import Sum, F, Q, Subquery, OuterRef, When, Case, DecimalField

from src.user.enums import WorkerIncomeType, WorkerIncomeReason
from src.order.enums import OrderStatus
from src.order.models import OrderItem, OrderItemProductFactory, Order, Client
from src.payment.models import Payment, Outlay
from src.payment.enums import PaymentType
from src.user.models import WorkerIncomes
from src.warehouse.models import WarehouseProductWriteOff
from src.factory.enums import ProductFactoryStatus
from src.factory.models import ProductFactory

User = get_user_model()


def separate_number(value):
    value = int(value)
    separated_value = list(str(value))
    for x in range(int(len(separated_value) / 3)):
        separated_value.insert(len(separated_value) - (x + 1) * 4 + 1, ' ')

    return str().join(separated_value)


def get_summary_data():
    now = timezone.localtime()
    previous_day = now - datetime.timedelta(days=1)

    start_date = datetime.datetime.combine(previous_day.date(), datetime.time.min)
    end_date = datetime.datetime.combine(previous_day.date(), datetime.time.max)
    month_start_date = start_date.replace(day=1)

    celebration_clients = Client.objects.filter(full_name__icontains='*')
    flower_outlay_categories = Outlay.objects.filter(Q(industry__id=6) | Q(id=6))

    order_items = OrderItem.objects.filter(
        models.Q(order__created_at__gte=start_date)
        & models.Q(order__created_at__lte=end_date)
        & ~models.Q(order__status=OrderStatus.CANCELLED)
        & models.Q(order__is_deleted=False)
        & models.Q(product__category__industry_id=6)
    ).with_total_self_price().with_total_profit().with_returned_total_sum()

    order_items_product_factories = OrderItemProductFactory.objects.filter(
        models.Q(order__created_at__gte=start_date)
        & models.Q(order__created_at__lte=end_date)
        & ~models.Q(order__status=OrderStatus.CANCELLED)
        & models.Q(order__is_deleted=False)
        & models.Q(is_returned=False)
        & models.Q(product_factory__category__industry_id=6)
    ).with_total_self_price().with_total_profit()

    orders = Order.objects.filter(
        models.Q(order_items__in=order_items)
        | models.Q(order_item_product_factory_set__in=order_items_product_factories)
        & models.Q(debt__gt=0)
    ).distinct().annotate(
        flowers_sum=Coalesce(
            Coalesce(
                Subquery(
                    OrderItem.objects.filter(order_id=OuterRef('pk'), product__category__industry_id=6)
                    .with_returned_total_sum()
                    .values('order_id')
                    .annotate(amount_sum=Sum(F('total') - F('returned_total_sum'), default=0))
                    .values('amount_sum')[:1]
                ), 0, output_field=DecimalField()
            ) + Coalesce(
                Subquery(
                    OrderItemProductFactory.objects.filter(
                        order_id=OuterRef('pk'),
                        product_factory__category__industry_id=6,
                        is_returned=False
                    )
                    .values('order_id')
                    .annotate(amount_sum=Sum(F('price'), default=0))
                    .values('amount_sum')[:1]
                ), 0, output_field=DecimalField()
            ), 0, output_field=DecimalField()
        ),
    )
    worker_incomes = WorkerIncomes.objects.filter(
        models.Q(created_at__gte=start_date)
        & models.Q(created_at__lte=end_date)
    )

    order_items_aggs = order_items.aggregate(
        total_sale_sum=Sum(F('total') - F('returned_total_sum'), default=0),
        total_self_price_sum=Sum('total_self_price', default=0),
        total_shop_sale_sum=Sum(
            F('total') - F('returned_total_sum'),
            default=0,
            filter=~Q(order__client__in=celebration_clients)
        ),
        total_clients_sale_sum=Sum(
            F('total') - F('returned_total_sum'),
            default=0,
            filter=Q(order__client__in=celebration_clients)
        ),
        total_shop_self_price_sum=Sum(
            F('total_self_price'),
            default=0,
            filter=~Q(order__client__in=celebration_clients)
        ),
        total_clients_self_price_sum=Sum(
            F('total_self_price'),
            default=0,
            filter=Q(order__client__in=celebration_clients)
        )
    )
    order_items_factories_aggs = order_items_product_factories.aggregate(
        total_sale_sum=Sum(F('price'), default=0),
        total_self_price_sum=Sum('total_self_price', default=0),
        total_shop_sale_sum=Sum(
            F('price'),
            default=0,
            filter=~Q(order__client__in=celebration_clients)
        ),
        total_clients_sale_sum=Sum(
            F('price'),
            default=0,
            filter=Q(order__client__in=celebration_clients)
        ),
        total_shop_self_price_sum=Sum(
            F('total_self_price'),
            default=0,
            filter=~Q(order__client__in=celebration_clients)
        ),
        total_clients_self_price_sum=Sum(
            F('total_self_price'),
            default=0,
            filter=Q(order__client__in=celebration_clients)
        )
    )
    payments = Payment.objects.get_available().filter(
        models.Q(created_at__gte=start_date)
        & models.Q(created_at__lte=end_date)
        & models.Q(payment_type=PaymentType.OUTCOME)
        & models.Q(outlay__in=flower_outlay_categories)
    )
    outlays = (
        Outlay.objects.filter(payments__in=payments).distinct()
        .annotate(total_amount=Subquery(
            payments.filter(outlay_id=OuterRef('pk'))
            .values('outlay_id')
            .annotate(total_amount=Sum('amount', default=0))
            .values('total_amount')[:1]
        ))
    )
    today_written_of_factories = (
        ProductFactory.objects.get_available().filter(
            status=ProductFactoryStatus.WRITTEN_OFF,
            written_off_at__range=[start_date, end_date]
        )
    )
    month_written_of_factories = (
        ProductFactory.objects.get_available().filter(
            status=ProductFactoryStatus.WRITTEN_OFF,
            written_off_at__range=[month_start_date, end_date]
        )
    )
    today_written_of_products = WarehouseProductWriteOff.objects.get_available().filter(
        warehouse_product__product__category__industry=6,
        created_at__range=[start_date, end_date]
    ).distinct()
    month_written_of_products = WarehouseProductWriteOff.objects.get_available().filter(
        warehouse_product__product__category__industry=6,
        created_at__range=[month_start_date, end_date]
    ).distinct()

    total_worker_income_sum = worker_incomes.aggregate(
        total_sum=Sum(
            Case(
                When(income_type=WorkerIncomeType.OUTCOME, then=-F('total')),
                default=F('total')
            ), default=0
        )
    )['total_sum']
    total_salesmen_income_sum = worker_incomes.filter(reason=WorkerIncomeReason.PRODUCT_SALE).aggregate(
        total_sum=Sum(
            Case(
                When(income_type=WorkerIncomeType.OUTCOME, then=-F('total')),
                default=F('total')
            ), default=0
        )
    )['total_sum']
    total_florist_income_sum = worker_incomes.filter(
        reason__in=[WorkerIncomeReason.PRODUCT_FACTORY_SALE, WorkerIncomeReason.PRODUCT_FACTORY_CREATE]
    ).aggregate(
        total_sum=Sum(
            Case(
                When(income_type=WorkerIncomeType.OUTCOME, then=-F('total')),
                default=F('total')
            ), default=0
        )
    )['total_sum']

    total_sale_sum = order_items_aggs['total_sale_sum'] + order_items_factories_aggs['total_sale_sum']
    total_self_price_sum = order_items_aggs['total_self_price_sum'] \
                           + order_items_factories_aggs['total_self_price_sum']

    total_shop_sale_sum = order_items_aggs['total_shop_sale_sum'] + order_items_factories_aggs['total_shop_sale_sum']
    total_shop_self_price_sum = order_items_aggs['total_shop_self_price_sum'] \
                                + order_items_factories_aggs['total_shop_self_price_sum']

    total_celebration_sale_sum = order_items_aggs['total_clients_sale_sum'] \
                                 + order_items_factories_aggs['total_clients_sale_sum']
    total_celebration_self_price_sum = order_items_aggs['total_clients_self_price_sum'] \
                                       + order_items_factories_aggs['total_clients_self_price_sum']
    total_today_write_off_sum = today_written_of_factories.aggregate(
        self_price_sum=Sum('self_price', default=0)
    )['self_price_sum'] + today_written_of_products.aggregate(
        self_price_sum=Sum(F('count') * F('warehouse_product__self_price'), default=0)
    )['self_price_sum']
    total_month_write_off_sum = month_written_of_factories.aggregate(
        self_price_sum=Sum('self_price', default=0)
    )['self_price_sum'] + month_written_of_products.aggregate(
        self_price_sum=Sum(F('count') * F('warehouse_product__self_price'), default=0)
    )['self_price_sum']

    outlay_sum = payments.aggregate(
        total_sum=Sum('amount', default=0)
    )['total_sum']

    total_profit = total_sale_sum - total_self_price_sum - outlay_sum

    total_flowers_debt = 0
    for order in orders:
        total_flowers_debt += max(min(order.debt, order.flowers_sum), 0)

    return {
        "total_sale_sum": total_sale_sum,
        "total_self_price_sum": total_self_price_sum,
        "total_shop_sale_sum": total_shop_sale_sum,
        "total_shop_self_price_sum": total_shop_self_price_sum,
        "total_celebration_sale_sum": total_celebration_sale_sum,
        "total_celebration_self_price_sum": total_celebration_self_price_sum,
        "total_profit": total_profit,
        "total_worker_income_sum": total_worker_income_sum,
        "total_salesmen_income_sum": total_salesmen_income_sum,
        "total_florist_income_sum": total_florist_income_sum,
        "total_today_write_off_sum": total_today_write_off_sum,
        "total_month_write_off_sum": total_month_write_off_sum,
        "outlay_sum": outlay_sum,
        "total_flowers_debt": total_flowers_debt,
        "outlays": outlays,
    }


def get_debt_data():
    now = timezone.localtime()
    previous_day = now - datetime.timedelta(days=1)

    start_date = datetime.datetime.combine(previous_day.date(), datetime.time.min)
    end_date = datetime.datetime.combine(previous_day.date(), datetime.time.max)

    payment_method_map = {
        1: 0,  # cash
        2: 0,
        3: 0,
        4: 0,
        6: 0,
        7: 0,
        8: 0,
        9: 0,
        10: 0,
        11: 0,  # card methods
    }

    all_orders = Order.objects.get_available().filter(
        models.Q(debt__gt=0)
    ).annotate(
        flowers_sum=Coalesce(
            Coalesce(
                Subquery(
                    OrderItem.objects.filter(order_id=OuterRef('pk'), product__category__industry_id=6)
                    .with_returned_total_sum()
                    .values('order_id')
                    .annotate(amount_sum=Sum(F('total') - F('returned_total_sum'), default=0))
                    .values('amount_sum')[:1]
                ), 0, output_field=DecimalField()
            ) + Coalesce(
                Subquery(
                    OrderItemProductFactory.objects.filter(
                        order_id=OuterRef('pk'),
                        product_factory__category__industry_id=6,
                        is_returned=False
                    )
                    .values('order_id')
                    .annotate(amount_sum=Sum(F('price'), default=0))
                    .values('amount_sum')[:1]
                ), 0, output_field=DecimalField()
            ), 0, output_field=DecimalField()
        ),
    )

    total_flowers_debt = 0
    for order in all_orders:
        total_flowers_debt += max(min(order.debt, order.flowers_sum), 0)

    payments = Payment.objects.get_available().filter(
        models.Q(created_at__gte=start_date)
        & models.Q(created_at__lte=end_date)
        & models.Q(payment_type=PaymentType.INCOME)
        & models.Q(is_debt=True)
        & models.Q(order__isnull=False)
    )

    orders = Order.objects.filter(id__in=payments.values_list('order_id', flat=True)).annotate(
        nonflowers_sum=Coalesce(
            Coalesce(
                Subquery(
                    OrderItem.objects.filter(
                        Q(order_id=OuterRef('pk'))
                        & ~Q(product__category__industry_id=6)
                    )
                    .with_returned_total_sum()
                    .values('order_id')
                    .annotate(amount_sum=Sum(F('total') - F('returned_total_sum'), default=0))
                    .values('amount_sum')[:1]
                ), 0, output_field=DecimalField()
            ) + Coalesce(
                Subquery(
                    OrderItemProductFactory.objects.filter(
                        Q(order_id=OuterRef('pk'))
                        & ~Q(product_factory__category__industry_id=6)
                        & Q(is_returned=False)
                    )
                    .values('order_id')
                    .annotate(amount_sum=Sum(F('price'), default=0))
                    .values('amount_sum')[:1]
                ), 0, output_field=DecimalField()
            ), 0, output_field=DecimalField()
        ),
    )

    for payment in payments:
        previous_payments_sum = Payment.objects.get_available().filter(
            Q(order_id=payment.order_id)
            & (
                    Q(created_at__lt=payment.created_at)
                    | (Q(created_at=payment.created_at) & Q(id__lt=payment.id))
            )
            & ~Q(id=payment.id)
        ).aggregate(amount_sum=Sum('amount', default=0))['amount_sum']

        order = orders.get(pk=payment.order_id)

        nonflowers_remaining = max(order.nonflowers_sum - previous_payments_sum, 0)
        flowers_payed = max(payment.amount - nonflowers_remaining, 0)

        if payment.payment_method.pk in payment_method_map.keys():
            payment_method_map[payment.payment_method.pk] += flowers_payed

    cash_total = payment_method_map[1]
    card_total = sum(value for key, value in payment_method_map.items() if key != 1)

    return {
        'total_flowers_debt': total_flowers_debt + cash_total + card_total,
        'cash_total': cash_total,
        'card_total': card_total,
        'remain_debt': total_flowers_debt
    }


def send_summary_notification():
    try:
        summary = get_summary_data()
        outlays = summary['outlays']

        outlays_by_category = "\n".join(
            f"{i + 1}) {o.title}: {separate_number(o.total_amount)}" for i, o in enumerate(outlays))

        message = textwrap.dedent(f"""\
🎯 <b>Отчет по Продажам (Цветы)</b>

💰  <i>Общая сумма продаж:</i> {separate_number(summary['total_sale_sum'])} (СБ: {separate_number(summary['total_self_price_sum'])})
🏪  <i>Сумма продаж магазин:</i> {separate_number(summary['total_shop_sale_sum'])} (СБ: {separate_number(summary['total_shop_self_price_sum'])})
🎉  <i>Сумма продаж табрик:</i> {separate_number(summary['total_celebration_sale_sum'])} (СБ: {separate_number(summary['total_celebration_self_price_sum'])})

💼  <i>Общая начислений сотрудникам:</i> {separate_number(summary['total_worker_income_sum'])}
🛒  <i>Сумма начислений продавцам:</i> {separate_number(summary['total_salesmen_income_sum'])}
🌸  <i>Сумма начислений флористам:</i> {separate_number(summary['total_florist_income_sum'])}
💳  <i>Сумма долга:</i> {separate_number(summary['total_flowers_debt'])}
🗑  <i>Сумма списаний за сегодня:</i> {separate_number(summary['total_today_write_off_sum'])}
🗑  <i>Сумма списаний за месяц:</i> {separate_number(summary['total_month_write_off_sum'])}

📊 <b>Расходы по Категориям</b>

{outlays_by_category}
    
💸 <b>Общая сумма расходов:</b> {separate_number(summary['outlay_sum'])}

📈  <b>Общая Сумма прибыли:</b> {separate_number(summary['total_profit'])}
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

    except Exception as e:
        print(e)


def send_debt_notification():
    # try:
    payed_debt_summary = get_debt_data()

    message = textwrap.dedent(f"""\
💰  <b>Долги (цветы)</b>

💰   <i>Общая сумма долга:</i> {separate_number(payed_debt_summary['total_flowers_debt'])}
💵  <i>Оплачено наличными:</i> {separate_number(payed_debt_summary['cash_total'])}
💳  <i>Оплачено картой:</i> {separate_number(payed_debt_summary['card_total'])}
⚖️  <i>Остаток долга:</i> {separate_number(payed_debt_summary['remain_debt'])}
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

    # except Exception as e:
    #     print(e)


if __name__ == '__main__':
    send_summary_notification()
    send_debt_notification()
