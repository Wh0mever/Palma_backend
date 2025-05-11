import datetime
import locale
import os
import django
from decimal import Decimal

from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.utils.translation import activate

from src.user.enums import UserType, WorkerIncomeReason, WorkerIncomeType

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "PalmaCrm.settings"
)

django.setup()

User = get_user_model()

from src.user.models import WorkerIncomes


def pay_salary_to_workers():
    workers = User.objects.filter(
        models.Q(is_active=True)
        & ~models.Q(type=UserType.ADMIN)
        & models.Q(salary_amount__gt=0)
    )
    for worker in workers:
        worker.balance += worker.salary_amount
        worker.save()
        create_worker_income(worker, worker.salary_amount)


def create_worker_income(worker: User, total: Decimal):
    current_date = timezone.now()
    previous_month_date = current_date - datetime.timedelta(days=current_date.day)

    localized_date = timezone.localtime(previous_month_date)
    locale.setlocale(locale.LC_ALL, 'russian_russia')
    WorkerIncomes.objects.create(
        worker=worker,
        income_type=WorkerIncomeType.INCOME,
        reason=WorkerIncomeReason.SALARY,
        total=total,
        salary_info=f"Зарплата за {localized_date.strftime('%B')}"
    )


def main():
    pay_salary_to_workers()


main()
