import os
import pandas as pd

import django
from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import Sum
from django.utils import timezone

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "PalmaCrm.settings"
)

django.setup()

from src.warehouse.models import WarehouseProduct, WarehouseProductWriteOff
from src.product.models import Product
from src.income.models import Income, IncomeItem

User = get_user_model()


def process_product_inventarization(product: Product, actual_count, user: User, income: Income):
    in_stock = product.warehouse_products.all().aggregate(
        count_sum=Sum('count', default=0))['count_sum']

    count_diff = in_stock - actual_count

    with transaction.atomic():

        if count_diff > 0:
            while count_diff > 0:
                warehouse_product = product.warehouse_products.filter(count__gt=0).order_by('created_at').first()
                write_off_count = min(warehouse_product.count, count_diff)
                warehouse_product.count = max(warehouse_product.count - write_off_count, 0)
                warehouse_product.save()

                WarehouseProductWriteOff.objects.create(
                    warehouse_product=warehouse_product,
                    count=write_off_count,
                    comment="Инвентаризация",
                    created_user=user
                )

                count_diff -= write_off_count

        elif count_diff < 0:
            last_wh_product: WarehouseProduct = product.warehouse_products.order_by('-created_at').first()
            income_item = IncomeItem.objects.create(
                income=income,
                product=product,
                count=abs(count_diff),
                price=last_wh_product.self_price,
                sale_price=last_wh_product.sale_price,
                total=last_wh_product.self_price * abs(count_diff),
                total_sale_price=last_wh_product.sale_price * abs(count_diff)
            )
            income.total += income_item.total
            income.total_sale_price += income_item.total_sale_price
            income.save()


def read_products():
    user = User.objects.get(id=1)
    with transaction.atomic():
        income = Income.objects.create(provider_id=23, created_at=timezone.now(), created_user=user)
        excel_pd = pd.read_excel('palma.xlsx')
        products_row = [list(row[1]) for row in excel_pd.iterrows()]
        for row in products_row:
            code = row[2]
            product = Product.objects.get(code=code)
            count = int(row[5])
            print(product, count)
            process_product_inventarization(product, count, user, income)

read_products()