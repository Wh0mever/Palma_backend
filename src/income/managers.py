from django.db.models import Q

from src.base.managers import FlagsQuerySet
from src.user.enums import UserType


class IncomeQuerySet(FlagsQuerySet):
    def by_user_industry(self, user):
        if user.type in [UserType.ADMIN, UserType.INCOME_MANAGER]:
            return self
        if user.type == UserType.WAREHOUSE_MASTER:
            return self.filter(income_item_set__product__category__industry=user.industry).distinct()
        if not user.industry:
            return self.none()
        return self.filter(Q(created_user__industry=user.industry))


class ProviderQuerySet(FlagsQuerySet):
    def by_user_industry(self, user):
        if user.type in [UserType.ADMIN, UserType.INCOME_MANAGER]:
            return self
        if not user.industry:
            return self.none()
        return self.filter(created_user__industry=user.industry)

