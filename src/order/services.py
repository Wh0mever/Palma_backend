from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.db import models, transaction
from django.db.models.functions import Coalesce
from django.utils import timezone

from src.core.helpers import create_action_notification
from src.core.models import Settings as AppSettings
from src.factory.enums import ProductFactoryStatus
from src.factory.models import ProductFactory
from src.order.enums import OrderStatus
from src.order.exceptions import NotEnoughProductsInOrderItemError, OrderHasReturnError, RestoreTimeExceedError
from src.order.models import Order, OrderItem, OrderItemProductOutcome, OrderItemProductReturn, OrderItemProductFactory, \
    Client, ClientDiscountLevel
from src.payment.enums import PaymentType
from src.payment.models import Payment, PaymentMethod
from src.product.models import Industry
from src.user.enums import WorkerIncomeReason, UserType, WorkerIncomeType
from src.user.models import WorkerIncomes
from src.user.services import calculate_salesman_compensation_from_order, calculate_florist_compensation_from_order
from src.warehouse.exceptions import NotEnoughProductInWarehouseError
from src.warehouse.services import reload_product_from_order_to_warehouse, get_available_warehouse_products_by_product, \
    calculate_total_product_count_in_warehouse

User = get_user_model()


# ====================== Client ====================== #
def calculate_client_discount_percent(client: Client):
    client_orders_total_amount = Order.objects.get_available().filter(
        models.Q(client=client)
        & models.Q(status=OrderStatus.COMPLETED)
    ).aggregate(total_amount=models.Sum('amount', default=0))['total_amount']
    discount_level = ClientDiscountLevel.objects.filter(
        orders_sum_to__gte=client_orders_total_amount
    ).order_by('orders_sum_to').first()
    return discount_level.discount_percent if discount_level else 0


def update_client_discount_percent(client: Client):
    if client.auto_discount_percent_change_enabled:
        discount_percent = calculate_client_discount_percent(client)
        if discount_percent > client.discount_percent:
            client.discount_percent = discount_percent
            client.save(update_fields=['discount_percent'])


# ====================== Order ====================== #
def update_order_total(order_id):
    Order.objects.filter(pk=order_id).update(
        total=Coalesce(
            Coalesce(
                models.Subquery(
                    OrderItem.objects.filter(order_id=models.OuterRef('pk'))
                    .values('order_id')
                    .annotate(total_sum=models.Sum('total', default=0))
                    .values('total_sum')[:1]
                ), models.Value(0), output_field=models.DecimalField()
            ) + Coalesce(
                models.Subquery(
                    OrderItemProductFactory.objects.filter(order_id=models.OuterRef('pk'), is_returned=False)
                    .values('order_id')
                    .annotate(total_sum=models.Sum('price', default=0))
                    .values('total_sum')[:1]
                ), models.Value(0), output_field=models.DecimalField()
            ) - Coalesce(
                models.Subquery(
                    OrderItemProductReturn.objects.filter(order_id=models.OuterRef('pk'), is_deleted=False)
                    .values('order_id')
                    .annotate(total_sum=models.Sum('total', default=0))
                    .values('total_sum')[:1], output_field=models.DecimalField()
                ), models.Value(0)
            ), models.Value(0), output_field=models.DecimalField()
        )
    )


def update_order_debt(order_id):
    Order.objects.filter(pk=order_id).update(
        debt=models.F('total') - models.F('discount') - Coalesce(
            Coalesce(
                models.Subquery(
                    Payment.objects.get_available()
                    .filter(order_id=models.OuterRef('pk'), payment_type="INCOME")
                    .values('order_id')
                    .annotate(amount_sum=models.Sum('amount', default=0))
                    .values('amount_sum')[:1],
                    output_field=models.DecimalField()
                ), models.Value(0, output_field=models.DecimalField())
            ) - Coalesce(
                models.Subquery(
                    Payment.objects.get_available()
                    .filter(order_id=models.OuterRef('pk'), payment_type="OUTCOME")
                    .values('order_id')
                    .annotate(amount_sum=models.Sum('amount', default=0))
                    .values('amount_sum')[:1],
                    output_field=models.DecimalField()
                ), models.Value(0, output_field=models.DecimalField())
            ),
            models.Value(0, output_field=models.DecimalField())
        )
    )


def get_order_items_total_sum(order: Order):
    return order.order_items.all().aggregate(sum_total=models.Sum('total', default=0))['sum_total']


def get_order_item_returns_total_sum(order: Order):
    return OrderItemProductReturn.objects.get_available().filter(order=order) \
        .aggregate(sum_total=models.Sum('total', default=0))['sum_total']


def get_order_item_product_factories_total_sum(order: Order):
    return order.order_item_product_factory_set.filter(is_returned=False) \
        .aggregate(sum_total=models.Sum('price', default=0))['sum_total']


def update_order_status(order: Order, status, user):
    with transaction.atomic():
        if order.status == status:
            return

        if status == 'CANCELLED':
            reload_product_from_order_to_warehouse(order.pk)
            reload_product_factories_from_order_to_warehouse(order.pk)
            cancel_workers_incomes_from_order(order.pk)

            # create_action_notification(
            #     obj_name=str(order),
            #     action="Отмена",
            #     user=user.get_full_name(),
            #     details=f"Сумма: {order.total - order.discount}"
            # )
        elif status == 'COMPLETED':
            update_client_discount_percent(order.client)
        order.status = OrderStatus[status.upper()]
        order.save()


def delete_order(order, user):
    update_order_status(order, OrderStatus.CANCELLED, user)
    order.is_deleted = True
    order.save()


def process_order_cancel(order):
    reload_product_from_order_to_warehouse(order.pk)
    reload_product_factories_from_order_to_warehouse(order.pk)
    cancel_workers_incomes_from_order(order.pk)


def restore_order(order):
    # if order.status != OrderStatus.CANCELLED:
    #     process_order_cancel(order)

    has_returns = OrderItemProductReturn.objects.get_available().filter(order=order) \
                  or OrderItemProductFactory.objects.filter(is_returned=True, order=order)

    if has_returns:
        raise OrderHasReturnError

    # now = timezone.now()
    # if now - order.created_at >= timedelta(days=5):
    #     raise RestoreTimeExceedError

    order_items = order.order_items.all()
    order_item_factories = order.order_item_product_factory_set.all()
    for item in order_items:
        count = item.count
        allocate_products_from_warehouse(item, count)
    for item in order_item_factories:
        add_product_factory_to_order_item(item)

    order.status = OrderStatus.CREATED
    order.save()


def create_order_payments_after_complete(request, order_id, payments):
    from src.payment.services import create_order_payment

    for payment in payments:
        amount = Decimal(payment['amount'])
        payment_id = payment['id']
        payment = PaymentMethod.objects.get(pk=payment_id)

        if amount > 0:
            create_order_payment(
                order_id,
                payment_method=payment,
                payment_type=PaymentType.INCOME,
                amount=amount,
                created_user=request.user
            )


# ====================== OrderItem ====================== #
def get_returned_products_total_count(order_item):
    """Return the total count of returned products"""
    product_return_objects = OrderItemProductReturn.objects.filter(order_item=order_item, is_deleted=False)
    total_count = product_return_objects.aggregate(total_count=models.Sum('count', default=0))['total_count']
    return total_count


def get_remaining_product_count(order_item):
    """
    Return the remaining count of products in an order item
    after deducting the count of returned products.
    """
    total_returned = get_returned_products_total_count(order_item)
    return order_item.count - total_returned


def create_or_update_order_item(order, product, count):
    """
    Creates a new OrderItem object for the given order and product,
    or updates an existing one if it already exists.
    """
    order_item, created = OrderItem.objects.get_or_create(
        order=order,
        product=product,
        defaults={
            "count": count,
            "price": product.price,
            "total": product.price * count
        }
    )
    if not created:
        order_item.count += count
        order_item.total = order_item.price * order_item.count
        order_item.save()
    return order_item, created


def create_product_outcome(order_item, warehouse_product, product_count):
    """
    Creates a new OrderItemProductOutcome object,
    or updates an existing one if it already exists.
    """
    obj, created = OrderItemProductOutcome.objects.get_or_create(
        warehouse_product=warehouse_product,
        order_item=order_item,
        defaults={
            'count': product_count
        }
    )
    if not created:
        obj.count += product_count
        warehouse_product.count -= product_count
    else:
        warehouse_product.count -= obj.count
    obj.save()
    warehouse_product.save()


def create_order_product_outcomes(order_item, warehouse_products, product_count=None):
    """
    Creates OrderItemProductOutcome instances and updates warehouse counts.
    """
    remaining_count = product_count if product_count else order_item.count
    for warehouse_product in warehouse_products:
        remove_count = min(remaining_count, warehouse_product.count)
        create_product_outcome(order_item, warehouse_product, remove_count)
        remaining_count -= remove_count
        if remaining_count == 0:
            break


def allocate_products_from_warehouse(order_item, product_count=None):
    """Allocate products from warehouse to fulfill an order item."""
    warehouse_products = get_available_warehouse_products_by_product(order_item.product)
    total_products_in_warehouse = calculate_total_product_count_in_warehouse(warehouse_products)
    total_products_to_allocate = product_count if product_count else order_item.count

    if total_products_in_warehouse < total_products_to_allocate:
        raise NotEnoughProductInWarehouseError

    create_order_product_outcomes(order_item, warehouse_products, product_count)


def add_products_to_order(order, product, count):
    """Create OrderItem and allocate products from warehouse to Order"""
    order_item, created = create_or_update_order_item(order, product, count)
    if created:
        allocate_products_from_warehouse(order_item)
    else:
        allocate_products_from_warehouse(order_item, count)
    return order_item


def handle_order_item_count_change(order_item: OrderItem, new_count):
    diff = abs(order_item.count - new_count)
    if order_item.count < new_count:
        add_products_to_order(order_item.order, order_item.product, diff)
    elif order_item.count > new_count:
        return_products_from_order_item_to_warehouse(order_item, diff)
    order_item.count = new_count
    order_item.total = order_item.price * order_item.count
    order_item.save()


def handle_order_item_price_change(order_item: OrderItem, new_price: Decimal):
    if order_item.price != new_price:
        # total_without_discount = order_item.product.price * order_item.count
        total_with_discount = new_price * order_item.count
        discount = order_item.product.price - new_price
        order_item.price = new_price
        order_item.discount = discount
        order_item.total = total_with_discount
        order_item.save()


def process_products_to_warehouse_return(order_product_outcomes, products_return_count):
    """Returns products from order_product_outcomes to warehouse"""
    remaining_count = products_return_count
    total_self_price = 0
    for product_outcome in order_product_outcomes:
        return_count = min(remaining_count, product_outcome.count)

        wh_product = product_outcome.warehouse_product
        wh_product.count += return_count
        wh_product.save()

        product_outcome.count -= return_count
        if product_outcome.count == 0:
            product_outcome.delete()
        else:
            product_outcome.save()

        remaining_count -= return_count
        total_self_price += wh_product.self_price * return_count
        if remaining_count == 0:
            break
    return total_self_price


def return_products_from_order_item_to_warehouse(order_item, products_return_count):
    """Return specific amount of products from orderItem to warehouse"""
    if not can_return_products(order_item, products_return_count):
        raise NotEnoughProductsInOrderItemError
    order_product_outcomes = OrderItemProductOutcome.objects.filter(order_item=order_item).order_by('-id')
    total_self_price = process_products_to_warehouse_return(order_product_outcomes, products_return_count)
    return total_self_price


def cancel_products_return(order_item, product_return_obj, user):
    """Cancel products to warehouse return"""
    allocate_products_from_warehouse(order_item, product_return_obj.count)
    delete_order_item_product_return(product_return_obj, user)


def delete_product_returns_from_order(order: Order, user):
    """Delete all product returns from order"""
    returns = order.product_returns.all().get_available()
    for item in returns:
        delete_order_item_product_return(item, user)


def delete_order_item_product_return(product_return_obj: OrderItemProductReturn, user):
    """Set product_return_obj as deleted"""
    product_return_obj.is_deleted = True
    product_return_obj.deleted_user = user
    product_return_obj.save()


def update_order_item_discount_after_return_created(order_item: OrderItem):
    discount_per_item = order_item.discount / (order_item.count - order_item.product_returns.count() - 1)
    order_item.discount -= discount_per_item
    order_item.save(update_fields=('discount',))


def update_order_item_discount_after_return_cancelled(order_item: OrderItem):
    discount_per_item = order_item.discount / (order_item.count - order_item.product_returns.count() + 1)
    order_item.discount += discount_per_item
    order_item.save(update_fields=('discount',))


def can_return_products(order_item, return_count):
    """Check if it's possible to return the specified number of products."""
    order_item_remain_products = get_remaining_product_count(order_item)
    if return_count > order_item_remain_products:
        return False
    return True


# ====================== OrderItemProductFactory ====================== #

def add_product_factory_to_order(order: Order, product_factory: ProductFactory):
    order_item_product_factory = OrderItemProductFactory.objects.create(
        order=order,
        product_factory=product_factory,
        price=product_factory.price
    )
    product_factory.status = ProductFactoryStatus.SOLD
    product_factory.save()
    update_order_total(order.pk)
    update_order_debt(order.pk)
    return order_item_product_factory


def remove_product_factory_from_order_item(order_item_product_factory: OrderItemProductFactory):
    product = order_item_product_factory.product_factory
    product.status = ProductFactoryStatus.FINISHED
    product.save()


def add_product_factory_to_order_item(order_item_product_factory: OrderItemProductFactory):
    product = order_item_product_factory.product_factory
    if not product.status == ProductFactoryStatus.FINISHED:
        raise NotEnoughProductInWarehouseError
    product.status = ProductFactoryStatus.SOLD
    product.save()


def delete_order_item_product_factory(order_item_product_factory: OrderItemProductFactory):
    if not order_item_product_factory.is_returned:
        remove_product_factory_from_order_item(order_item_product_factory)
    order_item_product_factory.delete()
    update_order_total(order_item_product_factory.order_id)
    update_order_debt(order_item_product_factory.order_id)


def update_order_item_product_factory(order_item_product_factory: OrderItemProductFactory, price: Decimal):
    order_id = order_item_product_factory.order_id
    order_item_product_factory.discount = order_item_product_factory.product_factory.price - price
    order_item_product_factory.price = price
    order_item_product_factory.save()
    update_order_total(order_id)
    update_order_debt(order_id)
    return order_item_product_factory


def return_order_item_product_factory(order_item_product_factory: OrderItemProductFactory, user):
    with transaction.atomic():
        order_item_product_factory.is_returned = True
        order_item_product_factory.returned_user = user
        order_item_product_factory.returned_at = timezone.now()
        order_item_product_factory.save()
        remove_product_factory_from_order_item(order_item_product_factory)
        cancel_florist_income_from_order(order_item_product_factory.order_id,
                                         order_item_product_factory.product_factory_id)
        update_order_total(order_id=order_item_product_factory.order_id)
        update_order_debt(order_id=order_item_product_factory.order_id)


def cancel_item_product_factory_return(order_item_product_factory: OrderItemProductFactory):
    with transaction.atomic():
        order_item_product_factory.is_returned = False
        order_item_product_factory.returned_user = None
        order_item_product_factory.returned_at = None
        order_item_product_factory.save()
        add_product_factory_to_order_item(order_item_product_factory)
        handle_compensation_to_florist_creation(
            order_item_product_factory.order,
            order_item_product_factory,
            order_item_product_factory.product_factory.florist
        )
        update_order_total(order_id=order_item_product_factory.order_id)
        update_order_debt(order_id=order_item_product_factory.order_id)


def reload_product_factories_from_order_to_warehouse(order_id):
    active_order_items = OrderItemProductFactory.objects.filter(order_id=order_id, is_returned=False)
    ProductFactory.objects.filter(order_item_set__in=active_order_items).update(
        status=ProductFactoryStatus.FINISHED
    )


# ====================== Workers ====================== #
def increase_worker_balance(user: User, amount: Decimal):
    user.balance += amount
    user.save()


def decrease_worker_balance(user: User, amount: Decimal):
    user.balance -= amount
    user.save()


def assign_compensation_from_orders_to_workers(order: Order, worker: User):
    assign_compensation_to_salesman(order, worker)
    assign_compensation_to_florists(order)


def assign_compensation_to_salesman(order: Order, worker: User):
    if worker and not worker.type in [UserType.ADMIN, UserType.NO_BONUS_SALESMAN, UserType.CASHIER]:
        compensation_amount, comment = calculate_salesman_compensation_from_order(order)
        if compensation_amount < 0:
            return
        increase_worker_balance(worker, compensation_amount)
        WorkerIncomes.objects.create(
            worker=worker,
            order=order,
            total=compensation_amount,
            income_type=WorkerIncomeType.INCOME,
            reason=WorkerIncomeReason.PRODUCT_SALE,
            comment=comment
        )


def assign_compensation_to_florists(order: Order):
    order_items = order.order_item_product_factory_set.select_related('product_factory__florist') \
        .filter(product_factory__florist__type=UserType.FLORIST_PERCENT)
    for item in order_items:
        florist = User.objects.get(pk=item.product_factory.florist_id)
        handle_compensation_to_florist_creation(order, item, florist)


def handle_compensation_to_florist_creation(order: Order, order_item: OrderItemProductFactory, florist: User):
    if florist.type != UserType.FLORIST_PERCENT:
        return
    compensation_amount, comment = calculate_florist_compensation_from_order(order_item)
    increase_worker_balance(florist, compensation_amount)
    WorkerIncomes.objects.create(
        worker=florist,
        order=order,
        product_factory=order_item.product_factory,
        total=compensation_amount,
        income_type=WorkerIncomeType.INCOME,
        reason=WorkerIncomeReason.PRODUCT_FACTORY_SALE,
        comment=comment
    )


def cancel_workers_incomes_from_order(order_id):
    cancel_salesman_income_from_order(order_id)

    order_item_product_factories = OrderItemProductFactory.objects.filter(order_id=order_id, is_returned=False)
    for item in order_item_product_factories:
        cancel_florist_income_from_order(order_id, item.product_factory_id)


def cancel_salesman_income_from_order(order_id):
    worker_income = WorkerIncomes.objects.filter(
        order=order_id,
        reason=WorkerIncomeReason.PRODUCT_SALE,
        income_type=WorkerIncomeType.INCOME
    ).first()
    if worker_income:
        worker = worker_income.worker
        decrease_worker_balance(worker, worker_income.total)
        WorkerIncomes.objects.create(
            worker=worker,
            order=worker_income.order,
            total=worker_income.total,
            income_type=WorkerIncomeType.OUTCOME,
            reason=WorkerIncomeReason.PRODUCT_SALE,
            comment="Отмена начисления продавцу за продажу товара"
        )


def reassign_salesman_compensation_from_order(order_id):
    order = Order.objects.get(pk=order_id)
    worker: User = order.salesman

    cancel_salesman_income_from_order(order.pk)
    worker.refresh_from_db(fields=['balance'])
    assign_compensation_to_salesman(order, worker)


def cancel_florist_income_from_order(order_id, product_factory_id):
    worker_income = WorkerIncomes.objects.filter(
        order=order_id,
        product_factory_id=product_factory_id,
        income_type=WorkerIncomeType.INCOME
    ).first()
    if worker_income:
        worker = worker_income.worker
        decrease_worker_balance(worker, worker_income.total)
        WorkerIncomes.objects.create(
            worker=worker,
            order=worker_income.order,
            product_factory=worker_income.product_factory,
            total=worker_income.total,
            income_type=WorkerIncomeType.OUTCOME,
            reason=WorkerIncomeReason.PRODUCT_FACTORY_SALE,
            comment=f"Отмена начисления флористу за продажу букета"
        )


def get_sale_percent(order: Order):
    app_settings = AppSettings.load()
    order_items = order.order_items.all().with_returned_count().filter(
        models.Q(product__category__industry__has_sale_compensation=True) &
        ~models.Q(count=models.F("returned_count"))
    ).values('product__category__industry').distinct()
    factory_order_items = order.order_item_product_factory_set.filter(
        is_returned=False
    ).values('product_factory__category__industry')
    industry = Industry.objects.get_available().filter(
        models.Q(pk__in=order_items) | models.Q(pk__in=factory_order_items)
    ).distinct()

    if not industry:
        return 0

    max_sale_percent = industry.order_by('-sale_compensation_percent').first().sale_compensation_percent
    return max_sale_percent
    # if order.order_items.filter(
    #         total__gt=0,
    #         product__category__industry__has_sale_compensation=True
    # ).distinct().exists():
    #     return app_settings.product_sale_commission_percentage
    # return app_settings.product_factory_sale_commission_percentage
