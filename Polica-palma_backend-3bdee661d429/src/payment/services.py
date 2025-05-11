from decimal import Decimal

from django.utils import timezone

from src.core.helpers import create_action_notification
from src.order.models import Order
from src.order.services import update_order_debt
from src.payment.enums import PaymentModelType, PaymentMethods, CashierType
from src.payment.exceptions import PaymentOrderDoesntExists, PaymentOutlayDoesntExists, PaymentIncomeDoesntExists, \
    PaymentProviderDoesntExists, DontHaveStartedShifts
from src.payment.models import Payment, Cashier, CashierShift


# =========================== COMMON =========================== #
def delete_payment(payment: Payment, user):
    payment.is_deleted = True
    payment.deleted_user = user
    payment.save()
    # create_action_notification(
    #     obj_name=str(payment),
    #     action="Удаление Платежа",
    #     user=user.get_full_name(),
    #     details=f"Тип платежа: {payment.get_payment_type_display()}.\n"
    #             f"Причина платежа: {payment.get_payment_model_type_display()}\n"
    #             f"Сумма: {payment.amount}"
    # )


def delete_outlay_payment(payment, user):
    if not payment.outlay:
        raise PaymentOutlayDoesntExists()
    delete_payment_from_cashier(payment)
    if payment.worker:
        delete_payment_from_worker(payment.worker, payment)
    delete_payment(payment, user)


def delete_income_payment(payment, user):
    if not payment.income:
        raise PaymentIncomeDoesntExists()
    delete_payment_from_provider(payment.provider, payment)
    delete_payment(payment, user)


def delete_provider_payment(payment, user):
    if not payment.provider:
        raise PaymentProviderDoesntExists()
    delete_payment_from_provider(payment.provider, payment)
    delete_payment(payment, user)


def delete_order_payment(payment, user):
    if not payment.order:
        raise PaymentOrderDoesntExists()
    delete_payment_from_order(payment.order, payment)
    delete_payment(payment, user)
    update_order_debt(payment.order_id)

# def update_payment(payment, amount, payment_method, payment_type, created_user, comment):
#     payment_model_type_map = {
#         'OUTLAY': update_outlay_payment,
#         'ORDER': update_order_payment,
#         'INCOME': update_provider_payment,
#         'PROVIDER': update_income_payment,
#     }
#     function = payment_model_type_map[payment.payment_model_type]
#     return function(payment, amount, payment_method, payment_type, created_user, comment)

# =========================== CASHIER =========================== #

def get_cashier_by_payment_method(payment_method):
    # method_to_cashier_map = {
    #     PaymentMethods.CASH: CashierType.CASH,
    #     PaymentMethods.TRANSFER_TO_CARD: CashierType.CARD,
    #     PaymentMethods.CARD: CashierType.BANK,
    #     PaymentMethods.TRANSFER: CashierType.BANK,
    # }
    cashier, is_created = Cashier.objects.get_or_create(payment_method=payment_method)
    return cashier


def add_payment_to_cashier(payment):
    cashier = get_cashier_by_payment_method(payment.payment_method)
    if payment.payment_type == "INCOME":
        process_income_payment_to_cashier(cashier, payment)
    else:
        process_outcome_payment_to_cashier(cashier, payment)


def delete_payment_from_cashier(payment):
    cashier = get_cashier_by_payment_method(payment.payment_method)
    if payment.payment_type == "INCOME":
        process_outcome_payment_to_cashier(cashier, payment)
    else:
        process_income_payment_to_cashier(cashier, payment)


def process_income_payment_to_cashier(cashier, payment):
    cashier.amount += payment.amount
    cashier.save()


def process_outcome_payment_to_cashier(cashier, payment):
    cashier.amount -= payment.amount
    cashier.save()


# =========================== Provider Payments =========================== #
def add_payment_to_provider(provider, payment):
    if payment.payment_type == "INCOME":
        process_income_payment_to_provider(provider, payment)
    else:
        process_outcome_payment_to_provider(provider, payment)
    add_payment_to_cashier(payment)


def delete_payment_from_provider(provider, payment):
    if payment.payment_type == "INCOME":
        process_outcome_payment_to_provider(provider, payment)
    else:
        process_income_payment_to_provider(provider, payment)
    delete_payment_from_cashier(payment)


def process_income_payment_to_provider(provider, payment):
    provider.balance += Decimal(payment.amount)
    provider.save()


def process_outcome_payment_to_provider(provider, payment):
    provider.balance -= Decimal(payment.amount)
    provider.save()


# =========================== Order Payments =========================== #

def create_order_payment(
        order_id,
        payment_method,
        payment_type,
        amount,
        created_user,
        comment=""
):
    order = Order.objects.get(pk=order_id)
    client = order.client
    payment = Payment.objects.create(
        order=order,
        client=client,
        payment_method=payment_method,
        payment_type=payment_type,
        payment_model_type=PaymentModelType.ORDER,
        amount=amount,
        created_user=created_user,
        comment=comment
    )
    add_payment_to_order(order, payment)
    return payment


def add_payment_to_order(order: Order, payment: Payment):
    # if payment.payment_type == "INCOME":
    #     process_income_payment_to_client(order.client, payment)
    # else:
    #     process_outcome_payment_to_client(order.client, payment)
    add_payment_to_cashier(payment)
    # update_order_debt(order.pk)


def delete_payment_from_order(order, payment):
    # if payment.payment_type == "INCOME":
    #     process_outcome_payment_to_client(order.client, payment)
    # else:
    #     process_income_payment_to_client(order.client, payment)
    delete_payment_from_cashier(payment)
    # update_order_debt(order.pk)


# =========================== Worker Payments =========================== #
def add_payment_to_worker(worker, payment):
    if payment.payment_type == "INCOME":
        process_income_payment_to_worker(worker, payment)
    else:
        process_outcome_payment_to_worker(worker, payment)
    # add_payment_to_cashier(payment)


def delete_payment_from_worker(worker, payment):
    if payment.payment_type == "INCOME":
        process_outcome_payment_to_worker(worker, payment)
    else:
        process_income_payment_to_worker(worker, payment)
    # delete_payment_from_cashier(payment)


def process_income_payment_to_worker(worker, payment):
    worker.balance += Decimal(payment.amount)
    worker.save()


def process_outcome_payment_to_worker(worker, payment):
    worker.balance -= Decimal(payment.amount)
    worker.save()


# =========================== Cashier Shift =========================== #
def close_cashier_shift(user):
    last_shift: CashierShift = (
        CashierShift.objects.filter(end_date__isnull=True, started_user=user)
        .with_total_income([user])
        .with_total_outcome([user])
        .with_total_income_cash([user])
        .with_total_outcome_cash([user])
        .by_started_user(user)
        .first()
    )
    if not last_shift:
        raise DontHaveStartedShifts
    last_shift.end_date = timezone.now()
    last_shift.completed_user = user
    last_shift.overall_income_amount = last_shift.total_income
    last_shift.overall_outcome_amount = last_shift.total_outcome
    last_shift.cash_income_amount = last_shift.total_income_cash
    last_shift.cash_outcome_amount = last_shift.total_outcome_cash
    last_shift.save()
