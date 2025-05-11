from decimal import Decimal

from django.db import models, transaction
from django.db.models.functions import Coalesce

from src.core.helpers import create_action_notification
from src.income.exceptions import IncompleteIncomeItemError
from src.payment.models import Payment
from src.payment.services import delete_payment_from_provider
from src.product.models import Product
from src.warehouse.services import create_or_update_warehouse_products, decrease_warehouse_products_count_by_income, \
    delete_warehouse_products_by_income
from src.warehouse.models import WarehouseProduct
from src.income.models import Income, IncomeItem, Provider
from src.income.enums import IncomeStatus


# ==================== PROVIDER ==================== #
def increase_provider_balance_by_income(income):  # noqa
    provider = income.provider
    provider.balance += income.total
    provider.save()


def decrease_provider_balance_by_income(income):
    provider = income.provider
    provider.balance -= income.total
    provider.save()


def update_provider_balance(provider_id):
    Provider.objects.filter(pk=provider_id).update(
        balance=Coalesce(
            models.Subquery(
                Payment.objects.get_available().filter(provider_id=models.OuterRef('pk'), payment_type="INCOME")
                .values('provider_id')
                .annotate(total_amount=models.Sum('amount', default=0))
                .values('total_amount')[:1]
            ), models.Value(0), output_field=models.DecimalField()
        ) - Coalesce(
            models.Subquery(
                Payment.objects.get_available().filter(provider_id=models.OuterRef('pk'), payment_type="OUTCOME")
                .values('provider_id')
                .annotate(total_amount=models.Sum('amount', default=0))
                .values('total_amount')[:1]
            ), models.Value(0), output_field=models.DecimalField()
        ) + Coalesce(
            models.Subquery(
                Income.objects.get_available().filter(provider_id=models.OuterRef('pk'))
                .filter(models.Q(status="ACCEPTED") | models.Q(status="COMPLETED"))
                .values('provider_id')
                .annotate(total_sum=models.Sum('total', default=0))
                .values('total_sum')[:1]
            ), models.Value(0), output_field=models.DecimalField()
        )
    )


# ==================== INCOME ==================== #

def income_update_total(income):
    income.total = IncomeItem.objects.filter(income=income).aggregate(
        total_sum=models.Sum('total', default=0)
    )['total_sum']
    income.save()


def income_update_total_sale_price(income_id):
    Income.objects.filter(pk=income_id).update(
        total_sale_price=Coalesce(
            models.Subquery(
                IncomeItem.objects.filter(income_id=models.OuterRef('pk'))
                .values('income_id')
                .annotate(total_sale_price_sum=models.Sum('total_sale_price', default=0))
                .values('total_sale_price_sum')[:1]
            ), models.Value(0), output_field=models.DecimalField()
        )
    )


def income_item_product_to_warehouse(income_item):
    warehouse_product = WarehouseProduct.objects.get(product=income_item.product)
    warehouse_product.count += income_item.count
    warehouse_product.save()


def update_income_status(income: Income, status, user):
    with transaction.atomic():
        if status == income.status:
            return
        if status == 'CREATED' and income.status == "CANCELLED":
            income.is_deleted = False
            income.save()
        if status == 'ACCEPTED':
            # if has_incomplete_income_items(income):
            #     raise IncompleteIncomeItemError
            increase_provider_balance_by_income(income)
        elif status == 'COMPLETED':
            create_or_update_warehouse_products(income)
        elif status == 'CANCELLED':
            if income.status != 'CREATED':
                decrease_provider_balance_by_income(income)
            if income.status == 'COMPLETED':
                delete_warehouse_products_by_income(income)
            # create_action_notification(
            #     obj_name=str(income),
            #     action="Отмена закупа",
            #     user=user.get_full_name(),
            #     details=f"Сумма закупа: {income.total}"
            # )

        income.status = IncomeStatus[status.upper()]
        income.save()


def has_incomplete_income_items(income):
    invalid_items_exists = income.income_item_set.filter(
        models.Q(count=0) |
        models.Q(sale_price=0) |
        models.Q(price=0)
    ).exists()
    return invalid_items_exists


def delete_income(income, user):
    update_income_status(income, IncomeStatus.CANCELLED, user)
    income.is_deleted = True
    income.save()



def create_or_update_income_item(income: Income, product: Product):
    obj, created = IncomeItem.objects.get_or_create(
        income=income,
        product=product,
        defaults={
            "income": income,
            "product": product,
            # "count": count,
            # "price": price,
            # "sale_price": sale_price,
            # "total": count * price,
            # "total_sale_price": count * sale_price,
        }
    )
    # if not created:
    #     obj.count += count
    #     obj.total = count * price
    #     obj.total_sale_price = count * sale_price
    #     obj.save()

    return obj, created
