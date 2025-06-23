from django.contrib import admin

from src.order.models import Order, OrderItem, Client, Department, OrderItemProductFactory, ClientDiscountLevel


@admin.register(ClientDiscountLevel)
class ClientDiscountLevelAdmin(admin.ModelAdmin):
    ...


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    ...


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'client', 'salesman', 'created_user', 'created_at')


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    pass


@admin.register(OrderItemProductFactory)
class OrderItemProductFactoryAdmin(admin.ModelAdmin):
    pass


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    pass
