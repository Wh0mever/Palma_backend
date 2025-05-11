from django.contrib import admin

from src.warehouse.models import WarehouseProduct, WarehouseProductWriteOff


@admin.register(WarehouseProduct)
class WarehouseProductAdmin(admin.ModelAdmin):
    list_display = ['id', 'product', 'count', 'self_price', 'sale_price']


@admin.register(WarehouseProductWriteOff)
class WarehouseProductWriteOffAdmin(admin.ModelAdmin):
    list_display = ['id', 'warehouse_product', 'count', 'created_at']