import os

import django
import requests

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "PalmaCrm.settings"
)

django.setup()

from django.conf import settings
from src.factory.models import FactoryTakeApartRequest

from src.core.enums import ActionPermissionRequestType
from src.core.models import ActionPermissionRequest, PermissionRequestTgMessage, Settings
from src.factory.enums import FactoryTakeApartRequestType
from src.warehouse.models import WarehouseProductWriteOff


def get_factory_perm_message(notification):
    message = ""
    if notification.request_type == FactoryTakeApartRequestType.TO_CREATE:
        message = f"РАЗОБРАТЬ.\n" \
                  f"Пользователь: {notification.created_user.first_name}\n" \
                  f"Букет #{notification.product_factory_id}"
    elif notification.request_type == FactoryTakeApartRequestType.WRITE_OFF:
        message = f"СПИСАТЬ.\n" \
                  f"Пользователь: {notification.created_user.first_name}\n" \
                  f"Букет #{notification.product_factory_id}"
    return message


def send_factory_perm_notifications():
    app_settings = Settings.load()

    notifications = FactoryTakeApartRequest.objects.filter(is_sent=False).order_by('created_at')
    for notification in notifications:
        message = get_factory_perm_message(notification)
        inline_keyboard = [
            [
                {'text': 'Подтвердить', 'callback_data': f'{notification.id}_yes'},
                {'text': 'Отклонить', 'callback_data': f'{notification.id}_no'}
            ]
        ]
        chat_ids = app_settings.permission_notification_receivers

        for chat_id in chat_ids:
            payload = {
                'chat_id': chat_id,
                'text': message,
                'reply_markup': {'inline_keyboard': inline_keyboard}
            }
            response = requests.post(
                url=f'{settings.TG_API_URL}{settings.PERMISSION_BOT_TOKEN}/sendMessage', json=payload
            )

            if response.status_code == 200:
                response_data = response.json()
                message_id = response_data.get('result', {}).get('message_id')
                if message_id:
                    PermissionRequestTgMessage.objects.create(
                        chat_id=chat_id,
                        message_id=message_id,
                        factory_permission_request=notification
                    )
                notification.is_sent = True
    FactoryTakeApartRequest.objects.bulk_update(notifications, ['is_sent'])


def get_perm_message(request):
    message = ""
    if request.request_type == ActionPermissionRequestType.PRODUCT_WRITE_OFF:
        write_off_obj = WarehouseProductWriteOff.objects.get(id=request.wh_product_write_off_id)
        message = f"Списание Товара.\n" \
                  f"Товар: {write_off_obj.warehouse_product.product.name}\n" \
                  f"Пользователь: {write_off_obj.created_user.first_name}\n" \
                  f"Кол-во: {write_off_obj.count}\n" \
                  f"Сумма списания: {write_off_obj.warehouse_product.self_price * write_off_obj.count}\n" \
                  f"Коментарий: {write_off_obj.comment}"
    return message


def send_perm_notifications():
    app_settings = Settings.load()
    
    notifications = ActionPermissionRequest.objects.filter(is_sent=False).order_by('created_at')
    for notification in notifications:
        message = get_perm_message(notification)
        inline_keyboard = [
            [
                {'text': 'Подтвердить', 'callback_data': f'{notification.id}_yes2'},
                {'text': 'Отклонить', 'callback_data': f'{notification.id}_no2'}
            ]
        ]
        chat_ids = app_settings.permission_notification_receivers

        for chat_id in chat_ids:
            payload = {
                'chat_id': chat_id,
                'text': message,
                'reply_markup': {'inline_keyboard': inline_keyboard}
            }
            response = requests.post(
                url=f'{settings.TG_API_URL}{settings.PERMISSION_BOT_TOKEN}/sendMessage', json=payload
            )
            if response.status_code == 200:
                response_data = response.json()
                message_id = response_data.get('result', {}).get('message_id')
                if message_id:
                    PermissionRequestTgMessage.objects.create(
                        chat_id=chat_id,
                        message_id=message_id,
                        action_permission_request=notification
                    )
                notification.is_sent = True
    ActionPermissionRequest.objects.bulk_update(notifications, ['is_sent'])


def main():
    send_factory_perm_notifications()
    send_perm_notifications()


if __name__ == '__main__':
    main()
