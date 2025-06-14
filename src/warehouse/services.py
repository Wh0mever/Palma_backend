from decimal import Decimal
from typing import Optional

from django.db import models
from django.contrib.auth import get_user_model

from src.factory.models import ProductFactoryItem, ProductFactory
from src.income.models import IncomeItem
from src.order.models import OrderItem, OrderItemProductOutcome
from src.warehouse.exceptions import NotEnoughProductInWarehouseError
from src.warehouse.models import WarehouseProduct, WarehouseProductWriteOff

User = get_user_model()


def get_available_warehouse_products_by_product(product):
    """Fetch warehouse products related to the given product."""
    return WarehouseProduct.objects.filter(product=product, count__gt=0).order_by('created_at')


def calculate_total_product_count_in_warehouse(warehouse_products):
    """Calculate the total count of given warehouse products."""
    return warehouse_products.aggregate(total_count=models.Sum('count', default=0))['total_count']


def create_or_update_warehouse_products(income):
    income_items = IncomeItem.objects.filter(income=income)
    for income_item in income_items:
        WarehouseProduct.objects.create(
            product=income_item.product,
            self_price=income_item.price,
            sale_price=income_item.sale_price,
            count=income_item.count,
            income_item=income_item
        )
        product = income_item.product
        product.price = income_item.sale_price
        product.save(update_fields=['price'])


def decrease_warehouse_products_count_by_income(income):
    income_list = IncomeItem.objects.filter(income=income)
    for income_item in income_list:
        wp_obj = WarehouseProduct.objects.get(product=income_item.product, self_price=income_item.price)
        wp_obj.count -= income_item.count
        wp_obj.save()


def delete_warehouse_products_by_income(income):
    income_items = income.income_item_set.all()
    warehouse_products = WarehouseProduct.objects.filter(income_item__in=income_items)
    warehouse_products.delete()


def increase_warehouse_product_count(warehouse_product, count):
    warehouse_product.count += count
    warehouse_product.save()


def decrease_warehouse_product_count(warehouse_product, count):
    warehouse_product.count -= count
    warehouse_product.save()


def load_products_from_warehouse_to_order(order_id):
    order_items = OrderItem.objects.filter(order_id=order_id)
    for item in order_items:
        wh_product = item.warehouse_product
        remaining_count = wh_product.count - item.count
        if remaining_count < 0:
            raise NotEnoughProductInWarehouseError
        wh_product.count = remaining_count
        wh_product.save()


def reload_product_from_order_to_warehouse(order_id):
    order_items = OrderItem.objects.filter(order_id=order_id)
    product_outcomes = OrderItemProductOutcome.objects.filter(order_item__in=order_items)
    reload_product_from_outcomes_to_warehouse(product_outcomes)


def reload_product_from_order_item_to_warehouse(order_item):
    product_outcomes = OrderItemProductOutcome.objects.filter(order_item=order_item)
    reload_product_from_outcomes_to_warehouse(product_outcomes)


def reload_product_from_outcomes_to_warehouse(product_outcomes):
    for product_outcome in product_outcomes:
        wh_product = product_outcome.warehouse_product
        wh_product.count += product_outcome.count
        wh_product.save()
    product_outcomes.delete()


def load_product_from_warehouse_to_product_factory(product_factory_id):
    factory = ProductFactory.objects.get(pk=product_factory_id)
    factory_items = factory.product_factory_item_set.all()
    for item in factory_items:
        wh_product = item.warehouse_product
        wh_product.count -= item.count
        wh_product.save()


def reload_product_from_product_factory_to_warehouse(product_factory_id):
    product_factory_items = ProductFactoryItem.objects.filter(factory_id=product_factory_id)
    reload_product_from_product_factory_items_to_warehouse(product_factory_items)


def reload_product_from_product_factory_items_to_warehouse(product_factory_items):
    for item in product_factory_items:
        increase_warehouse_product_count(item.warehouse_product, item.count)


# ==================== WarehouseProductWriteOff ==================== #
def create_warehouse_product_write_off(
        warehouse_product_id: int,
        count: Decimal,
        comment: Optional[str],
        user: User
):
    warehouse_product = WarehouseProduct.objects.select_related('product').get(pk=warehouse_product_id)
    if warehouse_product.count < count:
        raise NotEnoughProductInWarehouseError

    warehouse_product.count -= count
    warehouse_product.save()

    obj = WarehouseProductWriteOff.objects.create(
        warehouse_product=warehouse_product,
        count=count,
        comment=comment,
        created_user=user
    )
    return obj


def delete_warehouse_product_write_off(warehouse_product_write_off_id: int, user: User):
    warehouse_product_write_off = WarehouseProductWriteOff.objects \
        .select_related('warehouse_product') \
        .get(pk=warehouse_product_write_off_id)

    warehouse_product = warehouse_product_write_off.warehouse_product
    warehouse_product.count += warehouse_product_write_off.count
    warehouse_product.save()

    set_warehouse_product_write_off_deleted(warehouse_product_write_off, user)


def set_warehouse_product_write_off_deleted(warehouse_product_write_off: WarehouseProductWriteOff, user: User):
    warehouse_product_write_off.is_deleted = True
    warehouse_product_write_off.deleted_user = user
    warehouse_product_write_off.save()
