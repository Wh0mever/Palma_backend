from django.contrib import admin

from src.payment.models import Payment, Outlay, Cashier, PaymentMethodCategory, PaymentMethod, CashierShift


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'amount',
        'payment_type',
        'payment_method',
        'payment_model_type',
        'created_at',
        'is_deleted',
        'deleted_user'
    )


@admin.register(Outlay)
class OutlayAdmin(admin.ModelAdmin):
    pass


@admin.register(Cashier)
class CashierAdmin(admin.ModelAdmin):
    pass


@admin.register(PaymentMethodCategory)
class PaymentMethodCategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
    list_display_links = ['id', 'name']


@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'category', 'is_active']
    list_display_links = ['id', 'name']


@admin.register(CashierShift)
class CashierShiftAdmin(admin.ModelAdmin):
    list_display = ['id', '__str__']
    list_display_links = ['id', '__str__']