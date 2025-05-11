from django.contrib import admin

from src.income.models import Income, IncomeItem, Provider


@admin.register(Provider)
class ProviderAdmin(admin.ModelAdmin):
    pass


@admin.register(Income)
class IncomeAdmin(admin.ModelAdmin):
    pass


@admin.register(IncomeItem)
class IncomeItemAdmin(admin.ModelAdmin):
    pass
