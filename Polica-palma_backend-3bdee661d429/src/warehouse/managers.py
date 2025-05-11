from django.db import models

from src.base.managers import FlagsQuerySet
from src.user.enums import UserType


class WarehouseProductQuerySet(models.QuerySet):
    def by_user_industry(self, user):
        if user.type == UserType.ADMIN:
            return self
        if not user.industry:
            return self.none()
        return self.filter(product__category__industry=user.industry)


class WarehouseProductWriteOffQuerySet(FlagsQuerySet):
    def by_user_industry(self, user):
        if user.type == UserType.ADMIN:
            return self
        if not user.industry:
            return self.none()
        return self.filter(warehouse_product__product__category__industry=user.industry)
