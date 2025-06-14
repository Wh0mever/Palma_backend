from decimal import Decimal
from typing import List

import pandas as pd
from django.db import transaction
from django.contrib.auth import get_user_model

from src.income.enums import IncomeStatus
from src.income.models import Income, IncomeItem, ProviderProduct, Provider
from src.income.services import income_update_total, income_update_total_sale_price
from src.product.enums import ProductUnitType
from src.product.helpers import generate_product_code
from src.product.models import Category, Product, Industry

User = get_user_model()


def get_halfs(n):
    half = n // 2
    remainder = n % 2
    if remainder == 0:
        return half, half
    else:
        return half + 1, half


class BaseExcelParser:
    def __init__(self, file_obj):
        self.file_obj = file_obj
        self.products_row: List[List[str]] = self.read_file()

    def read_file(self) -> List[List[str]]:
        excel_pd = pd.read_excel(self.file_obj)
        products_row = [list(row[1]) for row in excel_pd.iterrows()]
        return products_row


class ProductImporter(BaseExcelParser):
    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

    def process_products(self, industry):
        with transaction.atomic():
            for row in self.products_row:
                product_name = row[0].strip()
                category = row[1].strip()
                price = row[4]
                provider_name = row[5].strip()
                category, created = Category.objects.get_or_create(name=category, industry=industry)
                product, created = Product.objects.get_or_create(
                    name=product_name,
                    category=category,
                    price=price * 12750 if not pd.isna(price) else 0,
                    unit_type=ProductUnitType.PIECE,
                )
                if created:
                    product.code = generate_product_code(product)
                    product.save()

                if not pd.isna(provider_name):
                    provider, created = Provider.objects.get_or_create(full_name=provider_name, created_user=self.user)
                    ProviderProduct.objects.create(product=product, provider=provider)

    def create_income(self, industry, created_user):
        with transaction.atomic():

            for row in filter(lambda x: not pd.isna(x[2]), self.products_row):
                product_name = row[0].strip()
                category_name = row[1].strip()
                count = Decimal(row[2] if not pd.isna(row[2]) else 0)
                self_price = Decimal(row[3] if not pd.isna(row[3]) else 0)
                price = Decimal(row[4] if not pd.isna(row[4]) else 0)
                provider_name = row[5].strip()

                provider = Provider.objects.filter(full_name=provider_name).first()
                income, is_created = Income.objects.get_or_create(
                    provider=provider,
                    created_user=created_user
                )

                category = Category.objects.filter(name=category_name, industry=industry).first()
                product = Product.objects.filter(
                    name=product_name,
                    category=category,
                ).first()

                if count != 0:
                    IncomeItem.objects.get_or_create(
                        income=income,
                        product=product,
                        count=count,
                        price=self_price * 12750,
                        sale_price=price * 12750,
                        total=self_price * 12750 * count,
                        total_sale_price=price * 12750 * count,
                    )

                income_update_total(income)
                income_update_total_sale_price(income.pk)

    def delete_products(self, industry):
        for row in self.products_row:
            product_name = row[0].strip()
            category_name = row[1].strip()

            category = Category.objects.filter(name=category_name, industry=industry).first()
            if not category:
                continue
            product = Product.objects.filter(
                name=product_name,
                category=category,
            ).first()
            if product:
                product.delete()


class FlowerProductsImporter(BaseExcelParser):
    def __init__(self, user, category, **kwargs):
        super().__init__(**kwargs)
        self.user = user
        self.category = category

    def process_products(self):
        with transaction.atomic():
            for row in self.products_row:
                product_name = row[1].strip()
                price = row[4]
                providers = row[5:7]
                category_name = row[7].strip()

                category = Category.objects.get(
                    name=category_name
                )

                product = Product.objects.create(
                    category=category,
                    unit_type=ProductUnitType.PIECE,
                    name=product_name,
                    price=price
                )
                product.code = generate_product_code(product)
                product.save()

                for provider in providers:
                    if not pd.isna(provider):
                        name = provider.strip()
                        provider, created = Provider.objects.get_or_create(full_name=name, created_user=self.user)
                        ProviderProduct.objects.create(product=product, provider=provider)

    def create_incomes(self):
        with transaction.atomic():
            products_row = list(filter(lambda r: not (r[2] == 0 or pd.isna(r[2])), self.products_row))
            products_with_single_providers = list(filter(lambda r: pd.isna(r[6]), products_row))
            products_with_two_providers = list(filter(lambda r: not pd.isna(r[6]), products_row))
            for row in products_with_single_providers:
                product_name = row[1].strip()
                count = Decimal(row[2])
                self_price = Decimal(row[3])
                price = Decimal(row[4])
                provider_name = row[5].strip()

                product, _ = Product.objects.get_or_create(name=product_name)
                provider, _ = Provider.objects.get_or_create(full_name=provider_name)

                income, _ = Income.objects.get_or_create(
                    provider=provider,
                    status=IncomeStatus.CREATED,
                    created_user=self.user
                )
                IncomeItem.objects.create(
                    income=income,
                    product=product,
                    count=count,
                    price=self_price,
                    sale_price=price,
                    total=count * self_price,
                    total_sale_price=count * price,
                )

            for row in products_with_two_providers:
                product_name = row[1].strip()
                count = Decimal(row[2])
                self_price = Decimal(row[3])
                price = Decimal(row[4])
                provider_name1 = row[5].strip()
                provider_name2 = row[6].strip()
                count1, count2 = get_halfs(count)

                product, _ = Product.objects.get_or_create(name=product_name)
                provider1, _ = Provider.objects.get_or_create(full_name=provider_name1)
                provider2, _ = Provider.objects.get_or_create(full_name=provider_name2)

                income1, _ = Income.objects.get_or_create(
                    provider=provider1,
                    status=IncomeStatus.CREATED,
                    created_user=self.user
                )
                income2, _ = Income.objects.get_or_create(
                    provider=provider2,
                    status=IncomeStatus.CREATED,
                    created_user=self.user
                )
                IncomeItem.objects.create(
                    income=income1,
                    product=product,
                    count=count1,
                    price=self_price,
                    sale_price=price,
                    total=count1 * self_price,
                    total_sale_price=count1 * price,
                )
                IncomeItem.objects.create(
                    income=income2,
                    product=product,
                    count=count2,
                    price=self_price,
                    sale_price=price,
                    total=count2 * self_price,
                    total_sale_price=count2 * price,
                )
