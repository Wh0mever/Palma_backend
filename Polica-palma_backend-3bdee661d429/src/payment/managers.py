from django.db import models
from django.db.models.functions import Coalesce
from django.utils import timezone

from src.payment.enums import PaymentType
from src.user.enums import UserType


class CashierShiftQuerySet(models.QuerySet):
    def by_started_user(self, user):
        if user.type == UserType.ADMIN:
            return self
        return self.filter(started_user=user)


    def with_total_income(self, created_users=None):
        from src.payment.models import Payment
        base_filter = {
            'created_at__gte': models.OuterRef('start_date'),
            'created_at__lt': Coalesce(models.OuterRef('end_date'), timezone.now()),
            'payment_type': PaymentType.INCOME,
        }

        if created_users:
            base_filter['created_user__in'] = created_users

        subquery = models.Subquery(
            Payment.objects.get_available()
            .filter(**base_filter)
            .values('is_deleted')
            .annotate(total_income=models.Sum('amount', default=0))
            .values('total_income')[:1]
        )

        return self.annotate(
            total_income=Coalesce(subquery, models.Value(0), output_field=models.DecimalField())
        )

    def with_total_outcome(self, created_users=None):
        from src.payment.models import Payment
        base_filter = {
            'created_at__gte': models.OuterRef('start_date'),
            'created_at__lt': Coalesce(models.OuterRef('end_date'), timezone.now()),
            'payment_type': PaymentType.OUTCOME,
        }

        if created_users:
            base_filter['created_user__in'] = created_users

        subquery = models.Subquery(
            Payment.objects.get_available()
            .filter(**base_filter)
            .values('is_deleted')
            .annotate(total_income=models.Sum('amount', default=0))
            .values('total_income')[:1]
        )
        return self.annotate(
            total_outcome=Coalesce(subquery, models.Value(0), output_field=models.DecimalField())
        )

    def with_total_profit(self, created_users):
        return self.with_total_income(created_users).with_total_outcome(created_users).annotate(
            total_profit=models.F('total_income') - models.F('total_outcome')
        )

    def with_total_income_cash(self, created_users):
        from src.payment.models import Payment
        base_filter = {
            'created_at__gte': models.OuterRef('start_date'),
            'created_at__lt': Coalesce(models.OuterRef('end_date'), timezone.now()),
            'payment_type': PaymentType.INCOME,
            'payment_method__category__name': "Наличные"
        }

        if created_users:
            base_filter['created_user__in'] = created_users

        subquery = models.Subquery(
            Payment.objects.get_available()
            .filter(**base_filter)
            .values('is_deleted')
            .annotate(total_income=models.Sum('amount', default=0))
            .values('total_income')[:1]
        )
        return self.annotate(
            total_income_cash=Coalesce(subquery, models.Value(0), output_field=models.DecimalField())
        )

    def with_total_outcome_cash(self, created_users):
        from src.payment.models import Payment
        base_filter = {
            'created_at__gte': models.OuterRef('start_date'),
            'created_at__lt': Coalesce(models.OuterRef('end_date'), timezone.now()),
            'payment_type': PaymentType.OUTCOME,
            'payment_method__category__name': "Наличные"
        }

        if created_users:
            base_filter['created_user__in'] = created_users

        subquery = models.Subquery(
            Payment.objects.get_available()
            .filter(**base_filter)
            .values('is_deleted')
            .annotate(total_income=models.Sum('amount', default=0))
            .values('total_income')[:1]
        )
        return self.annotate(
            total_outcome_cash=Coalesce(subquery, models.Value(0), output_field=models.DecimalField())
        )

    def with_total_profit_in_cash(self, created_users):
        return self.with_total_income_cash(created_users).with_total_outcome_cash(created_users).annotate(
            total_profit_cash=models.F('total_income_cash') - models.F('total_outcome_cash')
        )
