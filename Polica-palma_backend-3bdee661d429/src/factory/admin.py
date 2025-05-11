from django.contrib import admin
from django.db import transaction
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import path

from src.core.models import PermissionRequestTgMessage
from src.factory.enums import ProductFactoryStatus, FactoryTakeApartRequestType
from src.factory.models import (
    ProductFactory,
    ProductFactoryItem,
    ProductFactoryCategory, FactoryTakeApartRequest
)
from src.factory.services import (
    return_to_create, write_off_product_factory
)


@admin.register(ProductFactory)
class ProductFactoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'is_deleted')


@admin.register(ProductFactoryItem)
class ProductFactoryItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'factory', 'warehouse_product', 'count', 'total_price', 'total_self_price')


@admin.register(ProductFactoryCategory)
class ProductFactoryCategory(admin.ModelAdmin):
    list_display = ('id', 'name', 'is_deleted')


@admin.register(FactoryTakeApartRequest)
class FactoryTakeApartRequestAdmin(admin.ModelAdmin):
    list_display = ['id', 'product_factory', 'is_sent', 'is_answered', 'is_accepted', 'request_type']

    perm_actions = {
        FactoryTakeApartRequestType.TO_CREATE: return_to_create,
        FactoryTakeApartRequestType.WRITE_OFF: write_off_product_factory,
    }

    def allow(self, request, object_id, *args, **kwargs):
        with transaction.atomic():
            take_apart_request = get_object_or_404(FactoryTakeApartRequest, pk=object_id)
            take_apart_request.is_accepted = True
            take_apart_request.is_answered = True

            try:
                product_factory = ProductFactory.objects.get(id=take_apart_request.product_factory_id)
            except ProductFactory.DoesNotExist:
                self.message_user(request, "Объект не существует!")
                return HttpResponseRedirect(request.META['HTTP_REFERER'])

            action = self.perm_actions[take_apart_request.request_type]
            if product_factory.status == ProductFactoryStatus.PENDING:
                is_succeed, message = action(product_factory)
                if not is_succeed:
                    self.message_user(request, message)
                    return HttpResponseRedirect(request.META['HTTP_REFERER'])

            take_apart_request.save()
            self.message_user(request, "Разрешение на разборку букета выдано")
            PermissionRequestTgMessage.objects.filter(
                factory_permission_request=take_apart_request
            ).delete()
        return HttpResponseRedirect(request.META['HTTP_REFERER'])

    def disallow(self, request, object_id, *args, **kwargs):
        with transaction.atomic():
            take_apart_request = get_object_or_404(FactoryTakeApartRequest, pk=object_id)
            take_apart_request.is_accepted = False
            take_apart_request.is_answered = True

            try:
                product_factory = ProductFactory.objects.get(id=take_apart_request.product_factory_id)
            except ProductFactory.DoesNotExist:
                self.message_user(request, "Объект не существует!")
                return HttpResponseRedirect(request.META['HTTP_REFERER'])

            product_factory.status = take_apart_request.initial_status
            product_factory.save()
            take_apart_request.save()
            self.message_user(request, "Запрос на разборку букета отклонен")
            PermissionRequestTgMessage.objects.filter(
                factory_permission_request=take_apart_request
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
            path('<int:object_id>/allow/', self.admin_site.admin_view(self.allow),
                 name='allow'),
            path('<int:object_id>/disallow/', self.admin_site.admin_view(self.disallow),
                 name='disallow'),
        ]
        return custom_urls + urls
