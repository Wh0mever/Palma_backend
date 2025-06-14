from django.contrib import admin
from django.db import transaction
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import path

from src.core.enums import ActionPermissionRequestType
from src.core.models import Settings, BotMessage, ActionPermissionRequest, PermissionRequestTgMessage
from src.warehouse.models import WarehouseProductWriteOff
from src.warehouse.services import delete_warehouse_product_write_off


@admin.register(Settings)
class SettingsAdmin(admin.ModelAdmin):
    fields = [
        # 'product_sale_commission_percentage',
        # 'product_factory_sale_commission_percentage',
        'store_product_factory_sale_commission_percentage',
        'showcase_product_factory_sale_commission_percentage',
        'congratulations_product_factory_sale_commission_percentage',
        'product_factory_create_commission_amount',
        # 'product_factory_charge_percent',
        'store_sweets_create_commission_amount',
        'congratulations_sweets_create_commission_amount',
        'write_off_permission_granted_industries',
        'permission_notification_receivers',
    ]


@admin.register(BotMessage)
class BotMessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_at', 'is_sent')


@admin.register(ActionPermissionRequest)
class ActionPermissionRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'request_type', 'created_at', 'is_sent', 'is_answered', 'is_accepted', 'created_user')

    def allow(self, request, object_id, *args, **kwargs):
        with transaction.atomic():
            permission_request = get_object_or_404(ActionPermissionRequest, pk=object_id)
            permission_request.is_accepted = True
            permission_request.is_answered = True

            permission_request.save()
            self.message_user(request, "Разрешение выдано")
            PermissionRequestTgMessage.objects.filter(
                action_permission_request=permission_request
            ).delete()
        return HttpResponseRedirect(request.META['HTTP_REFERER'])

    def disallow(self, request, object_id, *args, **kwargs):
        with transaction.atomic():
            permission_request = get_object_or_404(ActionPermissionRequest, pk=object_id)
            permission_request.is_accepted = False
            permission_request.is_answered = True

            if permission_request.request_type == ActionPermissionRequestType.PRODUCT_WRITE_OFF:
                write_off_obj: WarehouseProductWriteOff = WarehouseProductWriteOff.objects.get(
                    id=permission_request.wh_product_write_off_id)

                if not write_off_obj.is_deleted:
                    delete_warehouse_product_write_off(write_off_obj.pk, user=request.user)

            permission_request.save()
            self.message_user(request, "Запрос отклонен")
            PermissionRequestTgMessage.objects.filter(
                action_permission_request=permission_request
            ).delete()
        return HttpResponseRedirect(request.META['HTTP_REFERER'])

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['allow_btn'] = True
        extra_context['disallow_btn'] = True
        return super().change_view(request, object_id, form_url, extra_context=extra_context)

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('<int:object_id>/perm-allow/', self.admin_site.admin_view(self.allow),
                 name='perm-allow'),
            path('<int:object_id>/perm-disallow/', self.admin_site.admin_view(self.disallow),
                 name='perm-disallow'),
        ]
        return custom_urls + urls

