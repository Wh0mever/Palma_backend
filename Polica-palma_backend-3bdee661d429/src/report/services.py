from collections import defaultdict
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Case, When, Q, Exists, OuterRef
from django.db.models.functions import Coalesce
from django.utils import timezone

from src.factory.enums import ProductFactoryStatus
from src.factory.models import ProductFactoryItemReturn, ProductFactoryItem, ProductFactory
from src.income.enums import IncomeStatus
from src.income.models import IncomeItem, Income
from src.order.enums import OrderStatus
from src.order.models import OrderItemProductReturn, OrderItem, Order, OrderItemProductFactory
from src.payment.enums import PaymentType
from src.payment.models import Payment
from src.product.models import Product
from src.user.enums import WorkerIncomeType, UserType
from src.user.models import WorkerIncomes
from src.warehouse.models import WarehouseProductWriteOff

User = get_user_model()


def get_material_report_products(
        user,
        start_date=timezone.datetime(2000, 1, 1),
        end_date=timezone.now(),
        industry=None
):
    qs = Product.objects.get_available()
    qs = qs.select_related('category__industry')
    qs = qs.by_user_industry(user).with_in_stock()

    if industry:
        qs = qs.filter(category__industry=industry)

    qs = qs.annotate(
        total_income_in_range=get_total_product_income(start_date, end_date),
        total_outcome_in_range=get_total_product_outcome(start_date, end_date),
        total_income_after_range=get_total_product_income(end_date, timezone.now()),
        total_outcome_after_range=get_total_product_outcome(end_date, timezone.now()),
        total_income_before_range=get_total_product_income(timezone.datetime(1900, 1, 1), start_date),
        total_outcome_before_range=get_total_product_outcome(timezone.datetime(1900, 1, 1), start_date),
    ).annotate(
        before_count=Coalesce(
            models.F('total_income_before_range') - models.F('total_outcome_before_range'),
            models.Value(0), output_field=models.DecimalField()
        ),
        after_count=Coalesce(
            models.F('before_count') + models.F('total_income_in_range') - models.F('total_outcome_in_range'),
            models.Value(0), output_field=models.DecimalField()
        )
    )

    return qs


def get_total_product_income_sub(start_date, end_date):
    income_item_subquery = models.Subquery(
        IncomeItem.objects.filter(
            product_id=models.OuterRef('pk'),
            income__status=IncomeStatus.COMPLETED,
            income__is_deleted=False,
            income__created_at__gte=start_date,
            income__created_at__lte=end_date,
        )
        .values('product_id')
        .annotate(count_sum=models.Sum('count', default=0))
        .values('count_sum')[:1]
    )
    order_item_return_subquery = models.Subquery(
        OrderItemProductReturn.objects.filter(
            order_item__product_id=models.OuterRef('pk'),
            is_deleted=False,
            created_at__gte=start_date,
            created_at__lte=end_date
        )
        .values('order_item__product_id')
        .annotate(count_sum=models.Sum('count', default=0))
        .values('count_sum')[:1]
    )
    product_factory_items_return_subquery = models.Subquery(
        ProductFactoryItemReturn.objects
        .filter(
            factory_item__warehouse_product__product_id=models.OuterRef('pk'),
            is_deleted=False,
            created_at__gte=start_date,
            created_at__lte=end_date,
        )
        .values('factory_item__warehouse_product__product_id')
        .annotate(count_sum=models.Sum('count', default=0))
        .values('count_sum')[:1]
    )
    subqueries = [
        income_item_subquery,
        order_item_return_subquery,
        product_factory_items_return_subquery
    ]
    return sum(Coalesce(subquery, models.Value(0), output_field=models.DecimalField()) for subquery in subqueries)


def get_total_product_outcome_sub(start_date, end_date):
    order_items_subquery = models.Subquery(
        OrderItem.objects.filter(
            models.Q(product_id=models.OuterRef('pk')) &
            ~models.Q(order__status=OrderStatus.CANCELLED) &
            models.Q(order__created_at__gte=start_date) &
            models.Q(order__created_at__lte=end_date)
        )
        .values('product_id')
        .annotate(count_sum=models.Sum('count', default=0))
        .values('count_sum')[:1],
        output_field=models.DecimalField()
    )
    product_factory_items_subquery = models.Subquery(
        ProductFactoryItem.objects.filter(
            models.Q(warehouse_product__product_id=models.OuterRef('pk')) &
            models.Q(factory__is_deleted=False) &
            models.Q(factory__created_at__gte=start_date) &
            models.Q(factory__created_at__lte=end_date)
        )
        .values('warehouse_product__product_id')
        .annotate(count_sum=models.Sum('count', default=0))
        .values('count_sum')[:1],
        output_field=models.DecimalField()
    )
    write_offs_subquery = models.Subquery(
        WarehouseProductWriteOff.objects.filter(
            warehouse_product__product_id=models.OuterRef('pk'),
            is_deleted=False,
            created_at__gte=start_date,
            created_at__lte=end_date
        )
        .values('warehouse_product__product_id')
        .annotate(count_sum=models.Sum('count', default=0))
        .values('count_sum')[:1],
        output_field=models.DecimalField()
    )
    subqueries = [
        order_items_subquery,
        product_factory_items_subquery,
        write_offs_subquery
    ]
    return sum(Coalesce(subquery, models.Value(0), output_field=models.DecimalField()) for subquery in subqueries)


def get_total_product_income(start_date, end_date):
    return Coalesce(
        models.Sum(
            'income_items__count', filter=Q(
                income_items__income__status=IncomeStatus.COMPLETED,
                income_items__income__is_deleted=False,
                income_items__income__created_at__gte=start_date,
                income_items__income__created_at__lte=end_date,
            ), default=0
        ) + models.Sum(
            'order_items__product_returns__count', filter=Q(
                order_items__product_returns__is_deleted=False,
                order_items__product_returns__created_at__gte=start_date,
                order_items__product_returns__created_at__lte=end_date
            ), default=0
        ) + models.Sum(
            'warehouse_products__product_factory_item_set__product_returns__count', filter=Q(
                warehouse_products__product_factory_item_set__product_returns__is_deleted=False,
                warehouse_products__product_factory_item_set__product_returns__created_at__gte=start_date,
                warehouse_products__product_factory_item_set__product_returns__created_at__lte=end_date,
            ), default=0,
        ), 0, output_field=models.DecimalField(),
    )


def get_total_product_outcome(start_date, end_date):
    return Coalesce(
        models.Sum(
            'order_items__count', filter=Q(
                ~models.Q(order_items__order__status=OrderStatus.CANCELLED) &
                models.Q(order_items__order__created_at__gte=start_date) &
                models.Q(order_items__order__created_at__lte=end_date)
            ), default=0
        ) + models.Sum(
            'warehouse_products__product_factory_item_set__count', filter=Q(
                models.Q(warehouse_products__product_factory_item_set__factory__is_deleted=False) &
                models.Q(warehouse_products__product_factory_item_set__factory__created_at__gte=start_date) &
                models.Q(warehouse_products__product_factory_item_set__factory__created_at__lte=end_date)
            ), default=0
        ) + models.Sum(
            'warehouse_products__product_write_off_set__count', filter=Q(
                warehouse_products__product_write_off_set__is_deleted=False,
                warehouse_products__product_write_off_set__created_at__gte=start_date,
                warehouse_products__product_write_off_set__created_at__lte=end_date
            ), default=0
        ), 0, output_field=models.DecimalField(),
    )


def get_material_report_orders(product: Product, start_date, end_date, industry=None):
    order_items = OrderItem.objects.filter(
        product=product
    )
    if industry:
        order_items = order_items.filter(product__category__industry_id=industry)
    return Order.objects.filter(
        models.Q(order_items__in=order_items) &
        ~models.Q(status=OrderStatus.CANCELLED) &
        models.Q(created_at__gte=start_date),
        models.Q(created_at__lte=end_date)
    ).distinct().annotate(
        product_count=Coalesce(
            models.Subquery(
                order_items.filter(order_id=models.OuterRef('pk'))
                .filter(product=product)
                .values('order_id')
                .annotate(count_sum=models.Sum('count', default=0))
                .values('count_sum')[:1]
            ), models.Value(0), output_field=models.DecimalField()
        ),
        total_product_sum=Coalesce(
            models.Subquery(
                order_items.filter(order_id=models.OuterRef('pk'))
                .filter(product=product).with_returned_total_sum()
                .values('order_id')
                .annotate(amount_sum=models.Sum(models.F('total') - models.F('returned_total_sum'), default=0))
                .values('amount_sum')[:1]
            ), models.Value(0), output_field=models.DecimalField()
        ),
        total_product_discount=Coalesce(
            models.Subquery(
                order_items.filter(order_id=models.OuterRef('pk'))
                .filter(product=product).with_total_discount()
                .values('order_id')
                .annotate(amount_sum=models.Sum(models.F('total_discount'), default=0))
                .values('amount_sum')[:1]
            ), models.Value(0), output_field=models.DecimalField()
        ),
        total_product_self_price=Coalesce(
            models.Subquery(
                order_items.filter(order_id=models.OuterRef('pk'))
                .filter(product=product).with_total_self_price()
                .values('order_id')
                .annotate(amount_sum=models.Sum(models.F('total_self_price'), default=0))
                .values('amount_sum')[:1]
            ), models.Value(0), output_field=models.DecimalField()
        ),
    ).select_related('created_user', 'client', 'salesman')


def get_material_report_incomes(product, start_date, end_date):
    income_items = IncomeItem.objects.filter(
        product=product
    )
    return Income.objects.get_available().filter(
        income_item_set__in=income_items,
        status=IncomeStatus.COMPLETED,
        created_at__gte=start_date,
        created_at__lte=end_date
    ).distinct().annotate(
        product_count=Coalesce(
            models.Subquery(
                income_items.filter(income_id=models.OuterRef('pk'))
                .values('income_id')
                .annotate(count_sum=models.Sum('count', default=0))
                .values('count_sum')[:1]
            ), models.Value(0), output_field=models.DecimalField()
        )
    ).select_related('created_user', 'provider')


def get_material_report_factories(product, start_date, end_date):
    product_factories = ProductFactoryItem.objects.filter(
        warehouse_product__product=product
    )
    return ProductFactory.objects.get_available().filter(
        product_factory_item_set__in=product_factories,
        created_at__gte=start_date,
        created_at__lte=end_date
    ).distinct().annotate(
        product_count=Coalesce(
            models.Subquery(
                product_factories.filter(factory_id=models.OuterRef('pk'))
                .values('factory_id')
                .annotate(count_sum=models.Sum('count', default=0))
                .values('count_sum')[:1]
            ), models.Value(0), output_field=models.DecimalField()
        )
    ).select_related('created_user', 'florist')


def get_material_report_write_offs(product, start_date, end_date):
    return WarehouseProductWriteOff.objects.get_available().filter(
        warehouse_product__product=product,
        created_at__gte=start_date,
        created_at__lte=end_date
    )


def get_material_report_order_item_returns(product, start_date, end_date):
    order_items = OrderItem.objects.filter(
        product=product
    )
    return OrderItemProductReturn.objects.get_available().filter(
        models.Q(order__status=OrderStatus.COMPLETED),
        models.Q(order_item__in=order_items) &
        models.Q(created_at__gte=start_date),
        models.Q(created_at__lte=end_date)
    ).distinct().select_related('created_user')


def get_material_report_factory_item_returns(product, start_date, end_date):
    return ProductFactoryItemReturn.objects.get_available().filter(
        factory_item__warehouse_product__product=product,
        created_at__gte=start_date,
        created_at__lte=end_date
    ).select_related('created_user').select_related('factory_item__factory')


# =================== WorkersReport =================== #
# def get_orders_count(start_date, end_date):
#     return Coalesce(
#         models.Subquery(
#             Order.objects.get_available()
#             .filter(
#                 salesman_id=models.OuterRef('pk'),
#                 status=OrderStatus.COMPLETED,
#                 created_at__gte=start_date,
#                 created_at__lte=end_date,
#             )
#             .values('salesman_id')
#             .annotate(total_count=models.Count('id'))
#             .values('total_count')[:1]
#         ), models.Value(0), output_field=models.DecimalField()
#     )


def get_orders_total_sum(start_date, end_date):
    return Coalesce(
        models.Subquery(
            Order.objects.get_available()
            .filter(
                salesman_id=models.OuterRef('pk'),
                status=OrderStatus.COMPLETED,
                created_at__gte=start_date,
                created_at__lte=end_date,
            )
            .with_total_with_discount()
            .values('salesman_id')
            .annotate(total_sum=models.Sum('total_with_discount', default=0))
            .values('total_sum')[:1]
        ), models.Value(0), output_field=models.DecimalField()
    )

# def get_orders_count(start_date, end_date):
#     return Coalesce(
#         models.Count(
#             'attached_orders__id', filter=Q(
#                 attached_orders__status=OrderStatus.COMPLETED,
#                 attached_orders__created_at__gte=start_date,
#                 attached_orders__created_at__lte=end_date,
#             ), distinct=True
#         ), models.Value(0), output_field=models.DecimalField()
#     )



def get_orders_count(start_date, end_date):
    orders_subquery = (
        Order.objects.filter(
            salesman_id=OuterRef('pk'),
            status=OrderStatus.COMPLETED,
            created_at__gte=start_date,
            created_at__lte=end_date
        ).values('salesman_id')
        .annotate(order_count=models.Count('id', distinct=True))
        .values('order_count')[:1]
    )
    return Coalesce(
        models.Subquery(orders_subquery),
        models.Value(0),
        output_field=models.DecimalField()
    )


def get_sold_products_sum(start_date, end_date):
    return Coalesce(
        models.Subquery(
            OrderItem.objects.filter(
                order__salesman_id=models.OuterRef('pk'),
                order__status=OrderStatus.COMPLETED,
                order__is_deleted=False,
                order__created_at__gte=start_date,
                order__created_at__lte=end_date,
            )
            .values('order__salesman_id')
            .annotate(total_sum=models.Sum('total', default=0))
            .values('total_sum')[:1]
        ), models.Value(0), output_field=models.DecimalField()
    )


def get_sold_product_factories_sum(start_date, end_date):
    return Coalesce(
        models.Subquery(
            OrderItemProductFactory.objects.filter(
                order__salesman_id=models.OuterRef('pk'),
                order__status=OrderStatus.COMPLETED,
                order__is_deleted=False,
                order__created_at__gte=start_date,
                order__created_at__lte=end_date,
            )
            .values('order__salesman_id')
            .annotate(total_sum=models.Sum('price', default=0))
            .values('total_sum')[:1]
        ), models.Value(0), output_field=models.DecimalField()
    )


def get_income_sum(start_date, end_date):
    return Coalesce(
        models.Subquery(
            WorkerIncomes.objects.filter(
                worker_id=models.OuterRef('pk'),
                created_at__gte=start_date,
                created_at__lte=end_date,
            )
            .values('worker_id')
            .annotate(total_sum=models.Sum(
                Case(
                    When(income_type=PaymentType.OUTCOME, then=-models.F('total')),
                    When(income_type=PaymentType.INCOME, then=models.F('total')),
                    default=0, output_field=models.DecimalField()
                ), default=0
            ))
            .values('total_sum')
        ), models.Value(0), output_field=models.DecimalField()
    )


def get_payment_sum(start_date, end_date):
    return Coalesce(
        models.Subquery(
            Payment.objects.get_available().filter(
                worker_id=models.OuterRef('pk'),
                created_at__gte=start_date,
                created_at__lte=end_date,
            )
            .values('worker_id')
            .annotate(total_sum=models.Sum(
                Case(
                    When(payment_type=PaymentType.OUTCOME, then=models.F('amount')),
                    When(payment_type=PaymentType.INCOME, then=-models.F('amount')),
                    default=0, output_field=models.DecimalField()
                ), default=0
            ))
            .values('total_sum')
        ), models.Value(0), output_field=models.DecimalField()
    )


def get_salesman_list(request, industry, start_date, end_date):
    salesman_list = User.objects.annotate(
        has_order=Exists(Order.objects.get_available().filter(salesman_id=OuterRef('pk')))
    ).filter(
        Q(type__in=[UserType.SALESMAN, UserType.NO_BONUS_SALESMAN])
        | Q(has_order=True)
        & Q(is_active=True)
    ).distinct() \
        .only('id', 'first_name', 'last_name', 'balance', 'industry')
    salesman_list = salesman_list.select_related('industry')
    if industry and industry not in [[], ['']]:
        salesman_list = salesman_list.filter(industry__in=industry)
    salesman_list = salesman_list.annotate(
        orders_count=get_orders_count(start_date, end_date),
        order_total_sum=get_orders_total_sum(start_date, end_date),
        income_sum=get_income_sum(start_date, end_date),
        payment_sum=get_payment_sum(start_date, end_date),
    )
    return salesman_list


def get_salesman_orders(salesman, start_date, end_date):
    return Order.objects.with_total_with_discount().filter(
        status=OrderStatus.COMPLETED,
        salesman=salesman,
        created_at__gte=start_date,
        created_at__lte=end_date,
    )


# =================== Workers =================== #
def get_worker_incomes(worker, start_date, end_date):
    return WorkerIncomes.objects.filter(
        worker=worker,
        created_at__gte=start_date,
        created_at__lte=end_date,
    )


def get_worker_payments(worker, start_date, end_date):
    return Payment.objects.get_available().filter(
        worker=worker,
        created_at__gte=start_date,
        created_at__lte=end_date,
    )


def get_other_worker_list(request, start_date, end_date):
    workers = User.objects.filter(
        type__in=[UserType.CASHIER, UserType.OTHER, UserType.WAREHOUSE_MASTER, UserType.FLORIST_ASSISTANT]
    )
    workers = workers.annotate(
        # income_sum=get_income_sum(start_date, end_date),
        payment_sum=get_payment_sum(start_date, end_date),
    )
    return workers


# =================== FloristReport =================== #
def get_factory_products_count(start_date, end_date, status):
    return Coalesce(
        models.Subquery(
            ProductFactory.objects.get_available().filter(
                florist_id=models.OuterRef('pk'),
                status__in=status,
                created_at__gte=start_date,
                created_at__lte=end_date,
            )
            .values('florist_id')
            .annotate(total_count=models.Count('id'))
            .values('total_count')[:1]
        ), models.Value(0), output_field=models.DecimalField()
    )


# def get_factory_products_count(start_date, end_date, status):
#     return Coalesce(
#         models.Count(
#             'owner_product_factory_set__id',
#             filter=Q(
#                 owner_product_factory_set__status=status,
#                 owner_product_factory_set__created_at__gte=start_date,
#                 owner_product_factory_set__created_at__lte=end_date,
#             ), distinct=True
#         ), models.Value(0), output_field=models.DecimalField()
#     )

def get_florist_list(request, start_date, end_date, industry):
    florist = User.objects.filter(
        type__in=[UserType.FLORIST, UserType.FLORIST_PERCENT, UserType.CRAFTER, UserType.FLORIST_ASSISTANT],
    )
    if industry:
        florist = florist.filter(industry__in=industry)
    return florist.annotate(
        sold_product_count=get_factory_products_count(start_date, end_date, [ProductFactoryStatus.SOLD]),
        finished_product_count=get_factory_products_count(
            start_date, end_date, [ProductFactoryStatus.FINISHED, ProductFactoryStatus.PENDING]),
        written_off_product_count=get_factory_products_count(start_date, end_date, [ProductFactoryStatus.WRITTEN_OFF]),
        income_sum=get_income_sum(start_date, end_date),
        payment_sum=get_payment_sum(start_date, end_date),
    )


def get_florist_product_factories(florist, status, start_date, end_date):
    factories = ProductFactory.objects.get_available().select_related('category').filter(
        florist_id=florist,
        created_at__gte=start_date,
        created_at__lte=end_date,
    )
    if status:
        factories = factories.filter(status__in=status)
    return factories


# =================== WorkersReport =================== #
def get_worker_list(start_date, end_date, industry):
    workers_list = User.objects.annotate(
        has_order=Exists(Order.objects.get_available().filter(salesman_id=OuterRef('pk')))
    ).filter(
        Q(is_active=True)
        & Q(
            Q(has_order=True)
            | Q(
                type__in=[
                    UserType.FLORIST, UserType.FLORIST_PERCENT, UserType.CRAFTER,
                    UserType.FLORIST_ASSISTANT, UserType.SALESMAN, UserType.MANAGER, UserType.NO_BONUS_SALESMAN,
                ]
            )
        )

    ).distinct()
    workers_list = workers_list.select_related('industry')

    if industry and industry not in [[], ['']]:
        workers_list = workers_list.filter(industry__in=industry)
    workers_list = workers_list.annotate(
        orders_count=get_orders_count(start_date, end_date),
        order_total_sum=get_orders_total_sum(start_date, end_date),
        sold_product_count=get_factory_products_count(start_date, end_date, [ProductFactoryStatus.SOLD]),
        finished_product_count=get_factory_products_count(start_date, end_date, [ProductFactoryStatus.FINISHED,
                                                                                 ProductFactoryStatus.PENDING]),
        written_off_product_count=get_factory_products_count(start_date, end_date, [ProductFactoryStatus.WRITTEN_OFF]),
        income_sum=get_income_sum(start_date, end_date),
        payment_sum=get_payment_sum(start_date, end_date),
    )

    return workers_list


# =================== WriteOffsReport =================== #

def get_write_offs_report_products(request, start_date, end_date):
    products = Product.objects.get_available().by_user_industry(request.user).with_in_stock() \
        .select_related('category__industry')

    products = products.annotate(
        product_count=get_write_off_count(start_date, end_date),
        self_price_sum=get_write_off_self_price_sum(start_date, end_date),
    ).filter(~models.Q(product_count=0))

    return products


def get_write_offs_report_product_factories(request, start_date, end_date):
    product_factories = ProductFactory.objects.get_available().select_related('category').filter(
        status=ProductFactoryStatus.WRITTEN_OFF,
        written_off_at__gte=start_date,
        written_off_at__lte=end_date
    )
    return product_factories


def get_product_write_offs(request, product, start_date, end_date):
    return WarehouseProductWriteOff.objects.get_available().filter(
        warehouse_product__product=product,
        created_at__gte=start_date,
        created_at__lte=end_date
    ).select_related('warehouse_product', 'created_user')


def get_write_off_count(start_date, end_date):
    return Coalesce(
        models.Subquery(
            WarehouseProductWriteOff.objects.get_available()
            .filter(warehouse_product__product_id=models.OuterRef('pk'))
            .filter(
                created_at__gte=start_date,
                created_at__lte=end_date,
            )
            .values('warehouse_product__product_id')
            .annotate(count_sum=models.Sum('count', default=0))
            .values('count_sum')[:1]
        ), models.Value(0), output_field=models.DecimalField()
    )


def get_write_off_self_price_sum(start_date, end_date):
    return Coalesce(
        models.Subquery(
            WarehouseProductWriteOff.objects.get_available()
            .filter(warehouse_product__product_id=models.OuterRef('pk'))
            .filter(
                created_at__gte=start_date,
                created_at__lte=end_date,
            )
            .values('warehouse_product__product_id')
            .annotate(total_sum=models.Sum(models.F('count') * models.F('warehouse_product__self_price'), default=0))
            .values('total_sum')[:1]
        ), models.Value(0), output_field=models.DecimalField()
    )


# =================== ClientsReport =================== #
def get_client_orders_count(start_date, end_date):
    return Coalesce(
        models.Subquery(
            Order.objects.get_available().filter(
                client_id=models.OuterRef('pk'),
                status=OrderStatus.COMPLETED,
                created_at__gte=start_date,
                created_at__lte=end_date,
            )
            .values('client_id')
            .annotate(total_count=models.Count('id'))
            .values('total_count')[:1]
        ), models.Value(0), output_field=models.DecimalField()
    )


def get_client_debt(start_date, end_date):
    return Coalesce(
        models.Subquery(
            Order.objects.get_available().filter(
                client_id=models.OuterRef('pk'),
                status=OrderStatus.COMPLETED,
                created_at__gte=start_date,
                created_at__lte=end_date,
            )
            .values('client_id')
            .annotate(debt_sum=models.Sum('debt'))
            .values('debt_sum')[:1]
        ), models.Value(0), output_field=models.DecimalField()
    )


def get_client_orders_sum(start_date, end_date):
    return Coalesce(
        models.Subquery(
            Order.objects.get_available().with_total_with_discount().filter(
                client_id=models.OuterRef('pk'),
                status=OrderStatus.COMPLETED,
                created_at__gte=start_date,
                created_at__lte=end_date,
            )
            .values('client_id')
            .annotate(total_sum=models.Sum('total_with_discount'))
            .values('total_sum')[:1]
        ), models.Value(0), output_field=models.DecimalField()
    )


def get_client_orders_discount_sum(start_date, end_date):
    return Coalesce(
        models.Subquery(
            Order.objects.get_available().with_total_discount().filter(
                client_id=models.OuterRef('pk'),
                status=OrderStatus.COMPLETED,
                created_at__gte=start_date,
                created_at__lte=end_date,
            )
            .values('client_id')
            .annotate(total_discount_sum=models.Sum('total_discount'))
            .values('total_discount_sum')[:1]
        ), models.Value(0), output_field=models.DecimalField()
    )


def get_clients_orders(request, client, start_date, end_date):
    return Order.objects.get_available().with_total_with_discount().with_total_discount() \
        .select_related('created_user', 'completed_user', 'salesman') \
        .filter(
        client=client,
        status=OrderStatus.COMPLETED,
        created_at__gte=start_date,
        created_at__lte=end_date,
    )


# =================== ProductFactoriesReport =================== #
def get_factories_report_product_factories(request, start_date, end_date):
    return (
        ProductFactory.objects.get_available()
        .select_related('florist', 'category__industry')
        .with_sold_price()
        .filter(created_at__gte=start_date, created_at__lte=end_date)
    )


# =================== ProductReturnsReport =================== #
def get_returns_report_product_returns(start_date, end_date):
    return OrderItemProductReturn.objects.get_available().filter(
        order__status=OrderStatus.COMPLETED,
        created_at__gte=start_date,
        created_at__lte=end_date
    ).select_related(
        'created_user',
        'order',
        'order_item__product'
    )


def get_returns_report_factories_returns(start_date, end_date):
    return OrderItemProductFactory.objects.filter(
        is_returned=True,
        order__status=OrderStatus.COMPLETED,
        returned_at__gte=start_date,
        returned_at__lte=end_date
    ).select_related(
        'returned_user',
        'order',
        'product_factory'
    )


# =================== OrderItemsReport =================== #

def get_order_items_report_products(start_date, end_date):
    return (
        OrderItem.objects.filter(
            models.Q(order__is_deleted=False) &
            ~models.Q(order__status=OrderStatus.CANCELLED),
            models.Q(order__created_at__gte=start_date),
            models.Q(order__created_at__lte=end_date)
        ).select_related('order__salesman', 'order__client', 'product__category__industry', 'order__created_user')
        .with_total_self_price()
        .with_total_discount()
        .with_total_charge()
        .with_total_profit()
        .with_returned_count()
        .with_returned_total_sum()
        .order_by('-order__created_at')
    )


def order_items_report_factories(start_date, end_date):
    return (
        OrderItemProductFactory.objects.filter(
            models.Q(order__is_deleted=False) &
            ~models.Q(order__status=OrderStatus.CANCELLED),
            models.Q(order__created_at__gte=start_date),
            models.Q(order__created_at__lte=end_date)
        ).select_related('order__salesman', 'order__client', 'product_factory__category__industry',
                         'order__created_user')
        .with_total_profit()
        .with_returned_count()
        .with_returned_total_sum()
        .with_total_self_price()
        .with_total_discount()
        .with_total_charge().annotate(
            total=models.F('price'),
            count=models.Case(
                models.When(is_returned=False, then=models.Value(1)),
                models.When(is_returned=True, then=models.Value(0)),
                default=models.Value(1), output_field=models.DecimalField()
            )
        ).filter(is_returned=False).order_by('-order__created_at')
    )

# =================== OverallReport =================== #
