from decimal import Decimal

from django.db import models
from django.db.models.functions import Coalesce
from django.utils import timezone

from src.core.models import Settings as AppSettings
from src.factory.enums import ProductFactorySalesType, ProductFactoryStatus, FactoryTakeApartRequestType
from src.factory.exceptions import NotEnoughProductInFactoryItemError
from src.factory.models import ProductFactory, ProductFactoryItem, ProductFactoryCategory, ProductFactoryItemReturn, \
    FactoryTakeApartRequest
from src.order.services import increase_worker_balance, decrease_worker_balance
from src.user.enums import WorkerIncomeReason, UserType, WorkerIncomeType
from src.user.models import WorkerIncomes
from src.warehouse.exceptions import NotEnoughProductInWarehouseError
from src.warehouse.models import WarehouseProduct
from src.warehouse.services import decrease_warehouse_product_count, increase_warehouse_product_count, \
    create_warehouse_product_write_off


# ================ ProductFactory ================ #
def update_product_factory_self_price(product_factory_id):
    ProductFactory.objects.filter(pk=product_factory_id).update(
        self_price=Coalesce(
            Coalesce(
                models.Subquery(
                    ProductFactoryItem.objects.filter(factory_id=models.OuterRef('pk'))
                    .values('factory_id')
                    .annotate(total_self_price_sum=models.Sum('total_self_price', default=0))
                    .values('total_self_price_sum')[:1]
                ), models.Value(0), output_field=models.DecimalField()
            ) - Coalesce(
                models.Subquery(
                    ProductFactoryItemReturn.objects.get_available()
                    .filter(factory_item__factory_id=models.OuterRef('pk'))
                    .values('factory_item__factory_id')
                    .annotate(total_self_price_sum=models.Sum('total_self_price', default=0))
                    .values('total_self_price_sum')[:1]
                ), models.Value(0), output_field=models.DecimalField()
            ), models.Value(0), output_field=models.DecimalField()
        )
    )


def update_product_factory_total_price(product_factory_id):
    ProductFactory.objects.filter(pk=product_factory_id).update(
        price=Coalesce(
            Coalesce(
                models.Subquery(
                    ProductFactoryItem.objects.filter(factory_id=models.OuterRef('pk'))
                    .values('factory_id')
                    .annotate(total_price_sum=models.Sum('total_price', default=0))
                    .values('total_price_sum')[:1]
                ), models.Value(0), output_field=models.DecimalField()
            ) - Coalesce(
                models.Subquery(
                    ProductFactoryItemReturn.objects.get_available()
                    .filter(factory_item__factory_id=models.OuterRef('pk'))
                    .values('factory_item__factory_id')
                    .annotate(total_price_sum=models.Sum('total_price', default=0))
                    .values('total_price_sum')[:1]
                ), models.Value(0), output_field=models.DecimalField()
            ), models.Value(0), output_field=models.DecimalField()
        )
    )


def write_off_product_factory(product_factory):
    if product_factory.status == ProductFactoryStatus.SOLD:
        return False, "Нельзя списать проданный товар"
    if product_factory.status == ProductFactoryStatus.PENDING:
        perm_request = FactoryTakeApartRequest.objects.filter(
            product_factory=product_factory,
            request_type=FactoryTakeApartRequestType.WRITE_OFF,
            is_answered=False,
        ).order_by('-id').first()
        if not perm_request:
            return False, 'Запрос на списание не найден'
        product_factory.status = perm_request.initial_status
    if product_factory.status == ProductFactoryStatus.FINISHED:
        remove_charge_from_product_factory(product_factory)
        cancel_product_factory_create_compensation_to_florist(product_factory)
        product_factory.refresh_from_db(fields=['price'])
    product_factory.status = ProductFactoryStatus.WRITTEN_OFF
    product_factory.written_off_at = timezone.now()
    product_factory.save()
    return True, ''


def return_to_create(product_factory):
    if product_factory.status not in [ProductFactoryStatus.FINISHED, ProductFactoryStatus.PENDING]:
        return False, "Букет должен быть завершен"

    product_factory.status = ProductFactoryStatus.CREATED
    product_factory.finished_at = None
    product_factory.finished_user = None
    product_factory.save()
    remove_charge_from_product_factory(product_factory)
    cancel_product_factory_create_compensation_to_florist(product_factory)
    return True, ''


# ================ ProductFactoryItem ================ #
def create_factory_item(
        factory: ProductFactory,
        warehouse_product: WarehouseProduct,
        count: Decimal
):
    product_factory_item, created = ProductFactoryItem.objects.get_or_create(
        factory=factory,
        warehouse_product=warehouse_product,
    )
    if created:
        product_factory_item.price = warehouse_product.sale_price
        product_factory_item.save()
    add_products_to_factory_item(product_factory_item, count)
    return product_factory_item


def update_factory_item(product_factory_item: ProductFactoryItem, count: Decimal):
    handle_product_factory_item_count_change(product_factory_item, count)


def handle_product_factory_item_count_change(product_factory_item: ProductFactoryItem, new_count: Decimal):
    current_count = product_factory_item.count
    diff = abs(current_count - new_count)
    if current_count < new_count:
        add_products_to_factory_item(product_factory_item, diff)
    elif current_count > new_count:
        remove_products_from_factory_item(product_factory_item, diff)


def add_products_to_factory_item(
        product_factory_item: ProductFactoryItem,
        product_count
):
    # product_add_count = product_count if product_count else product_factory_item.count
    warehouse_product = product_factory_item.warehouse_product
    if warehouse_product.count < product_count:
        raise NotEnoughProductInWarehouseError

    decrease_warehouse_product_count(warehouse_product, product_count)
    product_factory_item.count += product_count
    product_factory_item.total_self_price = product_factory_item.count * warehouse_product.self_price
    product_factory_item.total_price = product_factory_item.count * product_factory_item.price
    product_factory_item.save()


def remove_products_from_factory_item(
        product_factory_item: ProductFactoryItem,
        product_count
):
    # product_remove_count = product_count if product_count else product_factory_item.count
    warehouse_product = product_factory_item.warehouse_product
    if product_factory_item.count < product_count:
        raise NotEnoughProductInFactoryItemError

    increase_warehouse_product_count(warehouse_product, product_count)
    product_factory_item.count -= product_count
    product_factory_item.total_self_price = product_factory_item.count * warehouse_product.self_price
    product_factory_item.total_price = product_factory_item.count * product_factory_item.price
    product_factory_item.save()


def delete_product_factory_item(product_factory_item: ProductFactoryItem):
    increase_warehouse_product_count(product_factory_item.warehouse_product, product_factory_item.count)
    product_factory_item.delete()


def delete_factory_returns(factory_id, user):
    returns = ProductFactoryItemReturn.objects.get_available().filter(factory_item__factory_id=factory_id)
    for item in returns:
        cancel_products_return_from_factory_item(item, user)


def write_off_product_from_factory_item(factory_item: ProductFactoryItem, write_off_count: Decimal, user):
    remove_products_from_factory_item(factory_item, write_off_count)
    write_off_obj = create_warehouse_product_write_off(
        factory_item.warehouse_product.pk,
        write_off_count,
        comment=f"Списание из букета {str(factory_item.factory)}",
        user=user
    )
    if factory_item.count == 0:
        factory_item.delete()
    return write_off_obj


def calculate_product_factory_charge(product_factory: ProductFactory):
    factory_total_price = product_factory.get_items_total_sum()
    charge = factory_total_price * (product_factory.category.charge_percent / 100)
    return charge


def add_charge_to_product_factory(product_factory: ProductFactory):
    charge = calculate_product_factory_charge(product_factory)
    ProductFactory.objects.filter(pk=product_factory.id).update(
        price=models.F('price') + charge
    )


def remove_charge_from_product_factory(product_factory: ProductFactory):
    charge = calculate_product_factory_charge(product_factory)
    ProductFactory.objects.filter(pk=product_factory.id).update(
        price=models.F('price') - charge
    )


# ================ ProductFactoryCategory ================ #

def delete_product_factory_category(category: ProductFactoryCategory):
    category.is_deleted = True
    category.save()
    delete_factory_products_by_category(category)


def delete_factory_products_by_category(category: ProductFactoryCategory):
    ProductFactory.objects.filter(category=category).update(is_deleted=True)


# ======================== ProductFactoryReturn ======================== #
def get_factory_item_total_return_count(product_factory_item_id):
    return ProductFactoryItemReturn.objects.get_available().filter(factory_item_id=product_factory_item_id) \
        .aggregate(count_sum=models.Sum('count', default=0))['count_sum']


def get_factory_item_remaining_count(product_factory_item_id):
    return ProductFactoryItem.objects.get(pk=product_factory_item_id).count \
        - get_factory_item_total_return_count(product_factory_item_id)


def return_products_from_factory_item(product_factory_item: ProductFactoryItem, count):
    remaining_count = get_factory_item_remaining_count(product_factory_item.pk)
    if remaining_count < count:
        raise NotEnoughProductInFactoryItemError
    increase_warehouse_product_count(product_factory_item.warehouse_product, count)


def cancel_products_return_from_factory_item(product_factory_item_return: ProductFactoryItemReturn, user):
    warehouse_product = product_factory_item_return.factory_item.warehouse_product
    returned_count = product_factory_item_return.count

    if returned_count > warehouse_product.count:
        raise NotEnoughProductInWarehouseError
    decrease_warehouse_product_count(warehouse_product, returned_count)
    product_factory_item_return.is_deleted = True
    product_factory_item_return.deleted_user = user
    product_factory_item_return.save()


# ========================= Florist ========================= #
def get_compensation_amount_for_product_factory_create(product_factory: ProductFactory):
    app_settings = AppSettings.load()
    if product_factory.florist.type == UserType.FLORIST:
        return product_factory.florist.product_factory_create_commission
    elif product_factory.florist.type == UserType.CRAFTER:
        compensations_map = {
            ProductFactorySalesType.STORE.value: app_settings.store_sweets_create_commission_amount,
            ProductFactorySalesType.CONGRATULATION.value: app_settings.congratulations_sweets_create_commission_amount,
            ProductFactorySalesType.SHOWCASE.value: 0,
        }
        return compensations_map.get(product_factory.sales_type)


def assign_product_factory_create_compensation_to_florist(product_factory: ProductFactory):
    florist = product_factory.florist
    if florist.type in [UserType.FLORIST, UserType.CRAFTER]:
        last_income = WorkerIncomes.objects.filter(
            product_factory=product_factory, worker=florist, reason=WorkerIncomeReason.PRODUCT_FACTORY_CREATE
        ).order_by('-created_at').only('id', 'income_type').first()
        if last_income and last_income.income_type == WorkerIncomeType.INCOME:
            return
        compensation = get_compensation_amount_for_product_factory_create(product_factory)
        increase_worker_balance(florist, compensation)
        WorkerIncomes.objects.create(
            product_factory=product_factory,
            worker=florist,
            reason=WorkerIncomeReason.PRODUCT_FACTORY_CREATE,
            income_type=WorkerIncomeType.INCOME,
            total=compensation,
            comment=f"За создание букета.\n"
                    f"Букет: {product_factory.name}\n"
                    f"Флорист: {florist.get_full_name()}\n"
                    f"Сумма: {compensation}"
        )


def cancel_product_factory_create_compensation_to_florist(product_factory: ProductFactory):
    florist = product_factory.florist
    worker_income = WorkerIncomes.objects.filter(
        product_factory=product_factory,
        worker=florist,
        reason=WorkerIncomeReason.PRODUCT_FACTORY_CREATE,
        income_type=WorkerIncomeType.INCOME,
    ).first()
    if worker_income:
        compensation = worker_income.total
        decrease_worker_balance(florist, compensation)
        WorkerIncomes.objects.create(
            product_factory=product_factory,
            worker=florist,
            reason=WorkerIncomeReason.PRODUCT_FACTORY_CREATE,
            income_type=WorkerIncomeType.OUTCOME,
            total=compensation,
            comment=f"Отмена начисления за создание букета.\n"
                    f"Букет: {product_factory.name}\n"
                    f"Флорист: {florist.get_full_name()}\n"
                    f"Сумма: {compensation}"
        )
