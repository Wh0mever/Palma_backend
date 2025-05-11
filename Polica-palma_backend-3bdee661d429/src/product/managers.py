from django.db import models
from django.db.models.functions import Coalesce

from src.base.managers import FlagsQuerySet
from src.user.enums import UserType


class ProductQuerySet(FlagsQuerySet):
    def get_available(self):
        qs = super().get_available()
        return qs.select_related('category').filter(category__is_deleted=False)

    def with_in_stock(self):
        return self.prefetch_related('warehouse_products').annotate(
            in_stock=models.Sum('warehouse_products__count', default=0)
        )

    def by_user_industry(self, user):
        if user.type in [UserType.ADMIN, UserType.INCOME_MANAGER]:
            return self
        if not user.industry:
            return self.none()
        return self.filter(category__industry=user.industry)


class CategoryQuerySet(FlagsQuerySet):

    def by_user_industry(self, user):
        if user.type in [UserType.ADMIN, UserType.INCOME_MANAGER]:
            return self
        if not user.industry:
            return self.none()
        return self.filter(industry=user.industry)


class IndustryQuerySet(FlagsQuerySet):
    def by_user_industry(self, user):
        if user.type == UserType.ADMIN or user.type == UserType.CASHIER:
            return self
        if not user.industry:
            return self.none()
        return self.filter(pk=user.industry.pk)
