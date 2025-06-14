from django.contrib import admin
from django.contrib.auth import admin as user_admin

from src.user.models import User, WorkerIncomes


@admin.register(User)
class UserAdmin(user_admin.UserAdmin):
    list_display = ['id', 'username', 'first_name', 'last_name', 'balance', 'is_active']
    list_display_links = ['id', 'username']
    fieldsets = [
        (
            'Credentials',
            {
                "fields": ["username", "password"]
            }
        ),
        (
            'Personal Data',
            {
                "fields": [
                    "first_name", "last_name", "birthday", "avatar",
                    "balance", "salary_amount", "product_factory_create_commission"
                ]
            }
        ),
        (
            "User system data",
            {
                "fields": ["type", "industry", "groups", "user_permissions", "is_superuser", "is_staff", "is_active"]
            }
        )
    ]
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2'),
        }),
    )


@admin.register(WorkerIncomes)
class WorkerIncomesAdmin(admin.ModelAdmin):
    pass