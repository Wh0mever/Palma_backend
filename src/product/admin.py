from django.contrib import admin

from src.product.models import Product, Category, Industry


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'price', 'unit_type', 'code', 'category']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    pass


@admin.register(Industry)
class IndustryAdmin(admin.ModelAdmin):
    pass