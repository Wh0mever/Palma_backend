import datetime
import os

import django
from django.contrib.auth import get_user_model
from django.db import models, transaction
from django.utils import timezone

from src.order.enums import OrderStatus
from src.payment.enums import PaymentModelType, PaymentType

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "PalmaCrm.settings"
)

django.setup()

User = get_user_model()

from src.order.models import Client, Order
from src.payment.models import Payment, Cashier


def pay_clients_debts():
    clients_names = [
        'Пальма Табрик *',
        'BOBUR HUMO *',
        'Шохрух APELSIN табрик *',
        'Бехруз DIAMOND табрик *',
        'PALMA ТАБРИК *'
    ]
    client_ids = Client.objects.filter(full_name__in=clients_names).values_list('id', flat=True)

    end_date = datetime.datetime(2024, 7, 30, 0, 0, 0)
    user = User.objects.filter(is_active=True, is_superuser=True).first()

    orders = (
        Order.objects.get_available()
        .filter(
            models.Q(client_id__in=client_ids)
            & models.Q(status=OrderStatus.COMPLETED)
            & models.Q(created_at__lt=end_date)
            & models.Q(debt__gt=0)
            & ~models.Q(created_user__id=2)
        )
        .only('id', 'debt', 'client_id')
    )

    with transaction.atomic():
        cashier = Cashier.objects.filter(payment_method_id=1).first()
        payments = []
        for order in orders:
            payment = Payment.objects.create(
                payment_model_type=PaymentModelType.ORDER,
                payment_type=PaymentType.INCOME,
                payment_method_id=1,
                amount=order.debt,
                order_id=order.id,
                client_id=order.client_id,
                created_at=timezone.datetime(2024, 7, 29, 1, 0, 0),
                created_user=user,
                is_debt=True,
            )
            order.debt = 0
            order.save()
            payments.append(payment)
        Payment.objects.filter(pk__in=[p.id for p in payments]).update(created_at='2024-07-29')
        cashier.amount += sum(p.amount for p in payments)
        cashier.save()


pay_clients_debts()
