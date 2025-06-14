from django.db import models
from django.db.models.functions import Coalesce

from src.base.managers import FlagsQuerySet
from src.factory.enums import ProductFactoryStatus
from src.order.enums import OrderStatus
from src.order.models import OrderItemProductFactory
from src.user.enums import UserType


class ProductFactoryQuerySet(FlagsQuerySet):
    def with_sold_price(self):
        return self.annotate(
            sold_price=Coalesce(
                models.Subquery(
                    OrderItemProductFactory.objects.filter(product_factory_id=models.OuterRef('pk'))
                    .filter(
                        ~models.Q(order__status=OrderStatus.CANCELLED),
                        models.Q(is_returned=False)
                    ).values('price')[:1]
                ), models.Value(0), output_field=models.DecimalField()
            )
        )

    def by_user_industry(self, user):
        if user.type == UserType.ADMIN:
            return self
        if not user.industry:
            return self.none()
        return self.filter(category__industry=user.industry)

    def by_industry(self, industry):
        return self.filter(category__industry=industry)


class ProductFactoryCategoryQuerySet(FlagsQuerySet):
    def by_user_industry(self, user):
        if user.type == UserType.ADMIN:
            return self
        if not user.industry:
            return self.none()
        return self.filter(industry=user.industry)

    def by_industry(self, industry):
        return self.filter(industry=industry)


class ProductFactoryItemQuerySet(models.QuerySet):
    def with_returned_count(self):
        from src.factory.models import ProductFactoryItemReturn
        return self.annotate(
            returned_count=Coalesce(
                models.Subquery(
                    ProductFactoryItemReturn.objects.get_available()
                    .filter(factory_item_id=models.OuterRef('pk'))
                    .values('factory_item_id')
                    .annotate(total_count=models.Sum('count', default=0))
                    .values('total_count')[:1]
                ), models.Value(0), output_field=models.DecimalField()
            )
        )

    def with_returned_self_price_sum(self):
        from src.factory.models import ProductFactoryItemReturn
        return self.annotate(
            returned_self_price_sum=Coalesce(
                models.Subquery(
                    ProductFactoryItemReturn.objects.get_available()
                    .filter(factory_item_id=models.OuterRef('pk'))
                    .values('factory_item_id')
                    .annotate(total_self_price_sum=models.Sum('total_self_price', default=0))
                    .values('total_self_price_sum')[:1]
                ), models.Value(0), output_field=models.DecimalField()
            )
        )
