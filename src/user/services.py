from decimal import Decimal

from django.db import models
from django.contrib.auth import get_user_model

from src.core.models import Settings as AppSettings
from src.factory.enums import ProductFactorySalesType
from src.factory.models import ProductFactory
from src.order.models import Order, OrderItemProductFactory, OrderItemProductReturn
from src.user.enums import WorkerIncomeReason
from src.user.models import WorkerIncomes

User = get_user_model()



def create_worker_income_from_order_sale(
        worker: User,
        order: Order,
        total: Decimal
):
    WorkerIncomes.objects.create(
        worker=worker,
        order=order,
        total=total,
        reason=WorkerIncomeReason.PRODUCT_SALE,
    )


def calculate_salesman_compensation_for_products(order: Order):
    app_settings = AppSettings.load()
    items = order.order_items.all()
    return sum([item.total for item in items]) * Decimal(app_settings.product_sale_commission_percentage * 100)


def get_order_items_total_for_salesman_compensation(order: Order):
    order_items = order.order_items.filter(product__category__industry__has_sale_compensation=True).distinct()
    return order_items.aggregate(sum_total=models.Sum('total', default=0))['sum_total']


def get_factory_order_items_total_for_salesman_compensation(order: Order):
    return order.order_item_product_factory_set.filter(is_returned=False) \
        .aggregate(sum_total=models.Sum('price', default=0))['sum_total']


def get_order_item_returns_total_for_salesman_compensation(order: Order):
    return OrderItemProductReturn.objects.get_available().filter(
        order=order,
        order_item__product__category__industry__has_sale_compensation=True
    ).aggregate(sum_total=models.Sum('total', default=0))['sum_total']


def calculate_salesman_compensation_from_order(order: Order):
    from src.order.services import (
        get_sale_percent,
    )
    product_returns_total = get_order_item_returns_total_for_salesman_compensation(order)
    order_item_total = get_order_items_total_for_salesman_compensation(order)
    order_factory_total = get_factory_order_items_total_for_salesman_compensation(order)
    # compensation_for_products = calculate_salesman_compensation_for_products(order)
    # compensation_for_factories = calculate_salesman_compensation_for_factories(order)
    sale_total = order_item_total + order_factory_total - product_returns_total
    compensation_percent = get_sale_percent(order)
    compensation_total = sale_total * Decimal(compensation_percent / 100)
    comment = create_comment_for_order_sale_income(
        sale_total, compensation_percent, compensation_total
    )
    return compensation_total, comment


def create_comment_for_order_sale_income(sale_total: Decimal, percent: Decimal, income_total: Decimal):
    return f"Сумма: {sale_total:0.2f}\r\n" \
           f"Процент: {percent:0.2f}\r\n" \
           f"Начислено сотруднику: {income_total:0.2f}\r\n"


def get_florist_sale_compensation_percentage(product_factory: ProductFactory):
    app_settings = AppSettings.load()
    compensation_percentage_map = {
        ProductFactorySalesType.STORE.value: app_settings.store_product_factory_sale_commission_percentage,
        ProductFactorySalesType.SHOWCASE.value: app_settings.showcase_product_factory_sale_commission_percentage,
        ProductFactorySalesType.CONGRATULATION.value: app_settings.congratulations_product_factory_sale_commission_percentage,
    }
    return compensation_percentage_map.get(product_factory.sales_type)


def calculate_florist_compensation_from_order(order_item: OrderItemProductFactory):
    product_factory = order_item.product_factory
    compensation_percentage = get_florist_sale_compensation_percentage(product_factory)
    compensation_total = order_item.price * Decimal(compensation_percentage / 100)
    comment = create_comment_for_product_factory_sale_income(order_item.price, compensation_percentage,
                                                             compensation_total)
    return compensation_total, comment


def create_comment_for_product_factory_sale_income(sale_total: Decimal, percent: Decimal, income_total: Decimal):
    return f"Сумма: {sale_total:.2f}\r\n" \
           f"Процент: {percent:.2f}\r\n" \
           f"Начислено сотруднику: {income_total:.2f}\r\n"
