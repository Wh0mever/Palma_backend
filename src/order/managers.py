from django.db import models
from django.db.models import Case, When
from django.db.models.functions import Coalesce

from src.base.managers import FlagsQuerySet
from src.user.enums import UserType, WorkerIncomeReason, WorkerIncomeType


class OrderItemQuerySet(models.QuerySet):
    def with_returned_count(self):
        from src.order.models import OrderItemProductReturn
        return self.annotate(returned_count=Coalesce(
            models.Subquery(
                OrderItemProductReturn.objects.filter(order_item_id=models.OuterRef('pk'), is_deleted=False)
                .values('order_item_id')
                .annotate(total_count=models.Sum('count', default=0))
                .values('total_count')[:1]
            ), models.Value(0), output_field=models.DecimalField()
        ))

    def with_total_self_price(self):
        from src.order.models import OrderItemProductOutcome
        return self.annotate(total_self_price=Coalesce(
            models.Subquery(
                OrderItemProductOutcome.objects.filter(order_item_id=models.OuterRef('pk'))
                .values('order_item_id')
                .annotate(total_self_price=models.Sum(
                    models.F('warehouse_product__self_price') * models.F('count'), default=0)
                )
                .values('total_self_price')[:1]
            ), models.Value(0), output_field=models.DecimalField()
        ))

    def with_total_discount(self):
        from src.order.models import OrderItemProductReturn
        return self.annotate(
            total_discount=Coalesce(
                models.Case(
                    models.When(discount__gt=0, then=models.F('discount')),
                    default=models.Value(0), output_field=models.DecimalField()
                ) * (models.F('count') - Coalesce(
                    models.Subquery(
                        OrderItemProductReturn.objects.get_available().filter(order_item_id=models.OuterRef('pk'))
                        .values('order_item_id')
                        .annotate(returns_count=models.Sum('count', default=0))
                        .values('returns_count')[:1], output_field=models.DecimalField()
                    ), models.Value(0), output_field=models.DecimalField()
                )), models.Value(0), output_field=models.DecimalField()
            )
        )

    def with_total_charge(self):
        from src.order.models import OrderItemProductReturn
        return self.annotate(
            total_charge=Coalesce(
                models.Case(
                    models.When(discount__lt=0, then=-models.F('discount')),
                    default=models.Value(0), output_field=models.DecimalField()
                ) * (models.F('count') - Coalesce(
                    models.Subquery(
                        OrderItemProductReturn.objects.get_available().filter(order_item_id=models.OuterRef('pk'))
                        .values('order_item_id')
                        .annotate(returns_count=models.Sum('count', default=0))
                        .values('returns_count')[:1], output_field=models.DecimalField()
                    ), models.Value(0), output_field=models.DecimalField()
                )), models.Value(0), output_field=models.DecimalField()
            )
        )

    def with_total_profit(self):
        return self.with_total_self_price().with_returned_total_sum().annotate(
            total_profit=models.F('total') - models.F('returned_total_sum') - models.F('total_self_price')
        )

    def with_returned_total_sum(self):
        from src.order.models import OrderItemProductReturn
        return self.annotate(returned_total_sum=Coalesce(
            models.Subquery(
                OrderItemProductReturn.objects.get_available().filter(order_item_id=models.OuterRef('pk'))
                .values('order_item_id')
                .annotate(total_sum=models.Sum('total', default=0))
                .values('total_sum')[:1], output_field=models.DecimalField()
            ), models.Value(0), output_field=models.DecimalField()
        ))

    def by_industry(self, industry):
        return self.filter(product__category__industry=industry)

    def by_industries(self, industries):
        return self.filter(product__category__industry__in=industries)


class OrderItemProductFactoryQuerySet(models.QuerySet):
    def with_total_profit(self):
        return self.annotate(total_profit=models.F('price') - models.F('product_factory__self_price'))

    def with_returned_count(self):
        return self.annotate(returned_count=models.Case(
            models.When(is_returned=False, then=models.Value(0)),
            models.When(is_returned=True, then=models.Value(1)),
            default=models.Value(1), output_field=models.DecimalField()
        ))

    def with_returned_total_sum(self):
        return self.annotate(returned_total_sum=models.Case(
            models.When(is_returned=False, then=models.Value(0)),
            models.When(is_returned=True, then=models.F('price')),
            default=models.F('price'), output_field=models.DecimalField()
        ))

    def with_total_self_price(self):
        return self.annotate(total_self_price=models.F('product_factory__self_price'))

    def with_total_discount(self):
        return self.annotate(
            total_discount=models.Case(
                models.When(discount__gt=0, then=models.F('discount')),
                default=0,
                output_field=models.DecimalField()
            )
        )

    def with_total_charge(self):
        return self.annotate(
            total_charge=models.Case(
                models.When(discount__lt=0, then=-models.F('discount')),
                default=0,
                output_field=models.DecimalField()
            )
        )

    def by_industry(self, industry):
        return self.filter(product_factory__category__industry=industry)

    def by_industries(self, industries):
        return self.filter(product_factory__category__industry__in=industries)


class OrderQuerySet(FlagsQuerySet):
    def with_total_with_discount(self):
        return self.annotate(
            total_with_discount=models.F('total') - models.F('discount')
        )

    def with_amount_paid(self):
        from src.payment.models import Payment
        from src.payment.enums import PaymentType

        return self.annotate(
            amount_paid=Coalesce(
                models.Subquery(
                    Payment.objects.filter(
                        order_id=models.OuterRef('pk'),
                        is_deleted=False,
                    )
                    .values('order_id')
                    .annotate(amount_sum=models.Sum(
                        Case(
                            When(payment_type=PaymentType.OUTCOME, then=-models.F('amount')),
                            When(payment_type=PaymentType.INCOME, then=models.F('amount')),
                            default=0, output_field=models.DecimalField()
                        ), default=0
                    ))
                    .values('amount_sum')[:1]
                ), models.Value(0), output_field=models.DecimalField()
            )
        )

    def with_products_discount(self):
        from src.order.models import OrderItem, OrderItemProductFactory
        order_item_subquery = models.Subquery(
            OrderItem.objects.filter(order_id=models.OuterRef('pk'), discount__gt=0).with_total_discount()
            .values('order_id')
            .annotate(total_discount_sum=models.Sum('total_discount', default=0))
            .values('total_discount_sum')[:1]
        )
        order_item_product_factory_subquery = models.Subquery(
            OrderItemProductFactory.objects.filter(
                order_id=models.OuterRef('pk'),
                discount__gt=0,
                is_returned=False
            )
            .values('order_id')
            .annotate(total_discount=models.Sum('discount', default=0))
            .values('total_discount')[:1]
        )

        return self.annotate(
            products_discount=models.ExpressionWrapper(
                Coalesce(
                    order_item_subquery, models.Value(0),
                ) + Coalesce(
                    order_item_product_factory_subquery, models.Value(0),
                ), output_field=models.DecimalField()
            )
        )

    def with_total_discount(self):
        from src.order.models import OrderItem, OrderItemProductFactory
        order_item_subquery = models.Subquery(
            OrderItem.objects.filter(order_id=models.OuterRef('pk'), discount__gt=0).with_total_discount()
            .values('order_id')
            .annotate(total_discount_sum=models.Sum('total_discount', default=0))
            .values('total_discount_sum')[:1]
        )
        order_item_product_factory_subquery = models.Subquery(
            OrderItemProductFactory.objects.filter(
                order_id=models.OuterRef('pk'),
                discount__gt=0,
                is_returned=False,
            )
            .values('order_id')
            .annotate(total_discount=models.Sum('discount', default=0))
            .values('total_discount')[:1]
        )

        return self.annotate(
            total_discount=models.ExpressionWrapper(
                models.F('discount') + Coalesce(
                    order_item_subquery, models.Value(0),
                ) + Coalesce(
                    order_item_product_factory_subquery, models.Value(0),
                ), output_field=models.DecimalField()
            )
        )

    def with_total_charge(self):
        from src.order.models import OrderItem, OrderItemProductFactory
        order_item_subquery = models.Subquery(
            OrderItem.objects.filter(order_id=models.OuterRef('pk'), discount__lt=0).with_total_charge()
            .values('order_id')
            .annotate(total_charge_sum=models.Sum(models.F('total_charge'), default=0))
            .values('total_charge_sum')[:1]
        )
        order_item_product_factory_subquery = models.Subquery(
            OrderItemProductFactory.objects.filter(order_id=models.OuterRef('pk'), discount__lt=0)
            .values('order_id')
            .annotate(total_discount=models.Sum(-models.F('discount'), default=0))
            .values('total_discount')[:1]
        )

        return self.annotate(
            total_charge=models.ExpressionWrapper(
                Coalesce(
                    order_item_subquery, models.Value(0),
                ) + Coalesce(
                    order_item_product_factory_subquery, models.Value(0),
                ), output_field=models.DecimalField()
            )
        )

    def with_total_self_price(self):
        from src.order.models import OrderItem, OrderItemProductFactory

        order_item_subquery = models.Subquery(
            OrderItem.objects.filter(order_id=models.OuterRef('pk')).with_total_self_price()
            .values('order_id')
            .annotate(total_self_price_sum=models.Sum('total_self_price', default=0))
            .values('total_self_price_sum')[:1]
        )
        order_item_product_factory_subquery = models.Subquery(
            OrderItemProductFactory.objects.filter(is_returned=False, order_id=models.OuterRef('pk'))
            .values('order_id')
            .annotate(total_self_price=models.Sum('product_factory__self_price', default=0))
            .values('total_self_price')[:1]
        )
        return self.annotate(
            total_self_price=models.ExpressionWrapper(
                Coalesce(
                    order_item_subquery, models.Value(0),
                ) + Coalesce(
                    order_item_product_factory_subquery, models.Value(0),
                ), output_field=models.DecimalField()
            )
        )

    def with_total_profit(self):
        return self.with_total_with_discount().with_total_self_price().annotate(
            total_profit=models.F('total_with_discount') - models.F('total_self_price')
        )

    def with_total_debt(self):
        return self.annotate(
            total_debt=models.Sum('debt', default=0)
        )

    def with_industry(self):
        return self.annotate(
            industry=models.F('created_user__industry')
        )

    def by_user_industry(self, user):
        if user.type == UserType.ADMIN or user.type == UserType.SALESMAN:
            return self
        if not user.industry:
            return self.none()
        return self.filter(
            models.Q(order_items__product__category__industry=user.industry) |
            models.Q(order_item_product_factory_set__product_factory__category__industry=user.industry) |
            models.Q(salesman__industry=user.industry)
        ).distinct()

    def by_industry(self, industry):
        return self.filter(
            models.Q(order_items__product__category__industry=industry) |
            models.Q(order_item_product_factory_set__product_factory__category__industry=industry) |
            (
                    models.Q(order_items__isnull=True) &
                    models.Q(order_item_product_factory_set__isnull=True) &
                    models.Q(salesman__industry=industry)
            )
        ).distinct()

    def by_industries(self, industries):
        return self.filter(
            models.Q(order_items__product__category__industry__in=industries) |
            models.Q(order_item_product_factory_set__product_factory__category__industry__in=industries) |
            (
                    models.Q(order_items__isnull=True) &
                    models.Q(order_item_product_factory_set__isnull=True) &
                    models.Q(salesman__industry__in=industries)
            )
        ).distinct()


class ClientQuerySet(FlagsQuerySet):

    def with_debt(self):
        from .models import Order
        from .enums import OrderStatus
        return self.annotate(debt=Coalesce(
            models.Subquery(
                Order.objects.get_available()
                .filter(models.Q(client_id=models.OuterRef('pk')) & ~models.Q(status=OrderStatus.CANCELLED))
                .values('client_id')
                .annotate(debt=models.Sum('debt', default=0))
                .values('debt')[:1]
            ), models.Value(0), output_field=models.DecimalField())
        )

    def with_orders_count(self):
        from .models import Order
        from .enums import OrderStatus
        return self.annotate(
            orders_count=Coalesce(
                models.Subquery(
                    Order.objects.get_available()
                    .filter(models.Q(client_id=models.OuterRef('pk')) & ~models.Q(status=OrderStatus.CANCELLED))
                    .values('client_id')
                    .annotate(total_count=models.Count('id'))
                    .values('total_count')[:1]
                ), models.Value(0), output_field=models.DecimalField()
            )
        )

    def with_orders_total_sum(self):
        from .models import Order
        from .models import OrderStatus
        return self.annotate(
            total_orders_sum=Coalesce(
                models.Subquery(
                    Order.objects.get_available().with_total_with_discount()
                    .filter(models.Q(client_id=models.OuterRef('pk')) & ~models.Q(status=OrderStatus.CANCELLED))
                    .values('client_id')
                    .annotate(total_sum=models.Sum('total_with_discount', default=0))
                    .values('total_sum')[:1]
                ), models.Value(0), output_field=models.DecimalField()
            )
        )

    def with_orders_total_profit(self):
        from .models import Order
        from .models import OrderStatus
        return self.annotate(
            total_orders_profit_sum=Coalesce(
                models.Subquery(
                    Order.objects.get_available().with_total_profit()
                    .filter(models.Q(client_id=models.OuterRef('pk')) & ~models.Q(status=OrderStatus.CANCELLED))
                    .values('client_id')
                    .annotate(total_sum=models.Sum('total_profit', default=0))
                    .values('total_sum')[:1]
                ), models.Value(0), output_field=models.DecimalField()
            )
        )

    def with_order_total_sum_in_year(self):
        from .models import Order
        from .models import OrderStatus
        from src.core.helpers import get_year_range

        return self.annotate(
            total_orders_sum_in_year=Coalesce(
                models.Subquery(
                    Order.objects.get_available().with_total_with_discount()
                    .filter(
                        models.Q(client_id=models.OuterRef('pk'))
                        & ~models.Q(status=OrderStatus.CANCELLED)
                        & models.Q(created_at__range=[get_year_range()])
                    )
                    .values('client_id')
                    .annotate(total_sum=models.Sum('total_with_discount', default=0))
                    .values('total_sum')[:1]
                ), models.Value(0), output_field=models.DecimalField()
            )
        )

    def with_orders_count_in_year(self):
        from .models import Order
        from .enums import OrderStatus
        from src.core.helpers import get_year_range

        return self.annotate(
            orders_count_in_year=Coalesce(
                models.Subquery(
                    Order.objects.get_available()
                    .filter(
                        models.Q(client_id=models.OuterRef('pk'))
                        & ~models.Q(status=OrderStatus.CANCELLED)
                        & models.Q(created_at__range=[get_year_range()])
                    )
                    .values('client_id')
                    .annotate(total_count=models.Count('id'))
                    .values('total_count')[:1]
                ), models.Value(0), output_field=models.DecimalField()
            )
        )
