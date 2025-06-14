import datetime
import textwrap

import requests

from django.conf import settings
from django.db import models
from django.utils import timezone

from src.core.models import BotMessage
from src.payment.enums import PaymentType
from src.payment.models import Payment, PaymentMethod


def my_number_separator(value):
    value = int(value)
    separated_value = list(str(value))
    for x in range(int(len(separated_value) / 3)):
        separated_value.insert(len(separated_value) - (x + 1) * 4 + 1, ' ')

    return str().join(separated_value)


def try_parsing_date(text):
    date_formats = (
        '%Y-%m-%d',
        '%d.%m.%Y',
        '%d/%m/%Y',
        # '%m/%d/%Y',
        '%Y-%m-%d',
        # '%m.%d.%Y',
        '%d/%m/%Y %H:%M',
        '%d.%m.%Y %H:%M',
        '%Y-%m-%d %H:%M',
        # '%m/%d/%Y %H:%M',
        # '%m.%d.%Y %H:%M',
    )
    for fmt in date_formats:
        try:
            return datetime.datetime.strptime(text, fmt)
        except ValueError:
            pass
    raise ValueError('no valid date format found')


def create_action_notification(obj_name: str, action: str, user: str, details: str = ""):
    try:
        message = f"Объект: {obj_name}.\n" \
                  f"Действие: {action}.\n" \
                  f"Пользователь: {user}\n" \
                  f"{details}"
        BotMessage.objects.create(text=message)
    except Exception:
        print("Nevermind, shit happens")


def create_order_create_notification(order):
    payment_methods = PaymentMethod.objects.filter(payments__in=order.payments.filter(is_deleted=False)).distinct()
    payment_method_names = ", ".join([p.name for p in payment_methods]) if payment_methods else "-"
    message = textwrap.dedent(f"""
            📦 <b>Создан новый заказ №{order.pk}</b>

            🙋‍♂️ <i>Клиент</i>: {order.client.full_name}
            📞 <i>Номер клиента</i>: {order.client.phone_number}
            🛠️ <i>Создал</i>: {order.created_user.get_full_name()}
            🧑‍ <i>Продавец</i>: {order.salesman.get_full_name() if order.salesman else '-'}
            💰 <i>Сумма заказа</i>: {my_number_separator(order.get_total_with_discount())} Сум
            💳 <i>Долг</i>: {my_number_separator(order.debt)} Сум
            📉 <i>Общий долг клиента</i>: {my_number_separator(order.client.get_debt())} Сум
            💵 <i>Вид оплаты</i>: {payment_method_names}
        """)
    BotMessage.objects.create(text=message)


def create_order_cancel_notification(order):
    message = textwrap.dedent(f"""
                ❌ <b>Отменен заказ №{order.pk}</b>

                🙋‍♂️ <i>Клиент:</i> {order.client.full_name}
                📞 <i>Номер клиента:</i> {order.client.phone_number}
                🛠️ <i>Создал:</i> {order.created_user.get_full_name()}
                🧑‍ <i>Продавец:</i> {order.salesman.get_full_name() if order.salesman else '-'}
                💰 <i>Сумма заказа:</i> {my_number_separator(order.get_total_with_discount())} Сум
                ✅ <i>Оплачено:</i> {my_number_separator(order.get_amount_paid())} Сум
            """)
    BotMessage.objects.create(text=message)


def send_order_notification(order, created=True):
    payment_methods = PaymentMethod.objects.filter(payments__in=order.payments.filter(is_deleted=False)).distinct()
    payment_method_names = ", ".join([p.name for p in payment_methods]) if payment_methods else "-"
    message = textwrap.dedent(f"""
        📦 <b>Создан новый заказ №{order.pk}</b>
        
        🙋‍♂️ <i>Клиент</i>: {order.client.full_name}
        📞 <i>Номер клиента</i>: {order.client.phone_number}
        🛠️ <i>Создал</i>: {order.created_user.get_full_name()}
        🧑‍ <i>Продавец</i>: {order.salesman.get_full_name() if order.salesman else '-'}
        💰 <i>Сумма заказа</i>: {my_number_separator(order.get_total_with_discount())} Сум
        💳 <i>Долг</i>: {my_number_separator(order.debt)} Сум
        📉 <i>Общий долг клиента</i>: {my_number_separator(order.client.get_debt())} Сум
        💵 <i>Вид оплаты</i>: {payment_method_names}
    """)
    if not created:
        message = textwrap.dedent(f"""
            ❌ <b>Отменен заказ №{order.pk}</b>
            
            🙋‍♂️ <i>Клиент:</i> {order.client.full_name}
            📞 <i>Номер клиента:</i> {order.client.phone_number}
            🛠️ <i>Создал:</i> {order.created_user.get_full_name()}
            🧑‍ <i>Продавец:</i> {order.salesman.get_full_name() if order.salesman else '-'}
            💰 <i>Сумма заказа:</i> {my_number_separator(order.get_total_with_discount())} Сум
            ✅ <i>Оплачено:</i> {my_number_separator(order.get_amount_paid())} Сум
        """)
    payload = {
        'chat_id': settings.CHAT_ID,
        'text': message,
        'parse_mode': 'Html'
    }
    url = f"{settings.TG_API_URL}{settings.BOT_TOKEN}/sendMessage"
    requests.post(url, data=payload)


def create_daily_report_notification():
    try:
        now = timezone.now()
        start_date = datetime.datetime.combine(now.date(), datetime.time.min)
        end_date = datetime.datetime.combine(now.date(), datetime.time.max)

        today_income = Payment.objects.get_available().filter(
            payment_type=PaymentType.INCOME,
            created_at__gte=start_date,
            created_at__lte=end_date,
        ).aggregate(total_amount=models.Sum('amount', default=0))['total_amount']
        today_outcome = Payment.objects.get_available().filter(
            payment_type=PaymentType.OUTCOME,
            created_at__gte=start_date,
            created_at__lte=end_date,
        ).aggregate(total_amount=models.Sum('amount', default=0))['total_amount']
        today_profit = today_income - today_outcome

        message = f"Итоговая прибыль за сегодня: {today_profit} Сум"
        BotMessage.objects.create(text=message)
    except Exception:
        print("Nevermind, shit happens")
