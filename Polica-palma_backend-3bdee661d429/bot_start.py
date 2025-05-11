import asyncio
import os

import django
import requests
from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from dotenv import load_dotenv
from requests.auth import HTTPBasicAuth

load_dotenv()

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "PalmaCrm.settings")
django.setup()

from src.factory.models import FactoryTakeApartRequest, ProductFactory

from src.factory.enums import ProductFactoryStatus, FactoryTakeApartRequestType
from src.core.enums import ActionPermissionRequestType
from src.core.models import ActionPermissionRequest, PermissionRequestTgMessage
from src.warehouse.models import WarehouseProductWriteOff

# Bot token can be obtained via https://t.me/BotFather
# TOKEN = os.environ.get("BOT_TOKEN")
TOKEN = os.getenv('PERMISSION_BOT_TOKEN')
URL = os.getenv('PERMISSION_BOT_REQUEST_URL')
FACTORY_PERM_API_ENDPOINTS = {
    FactoryTakeApartRequestType.TO_CREATE: "{url}/factories/product-factories/{id}/return_to_create/",
    FactoryTakeApartRequestType.WRITE_OFF: "{url}/factories/product-factories/{id}/write_off/",

}
GENERAL_PERM_API_ENDPOINTS = {
    ActionPermissionRequestType.PRODUCT_WRITE_OFF: "{url}/warehouse/write-offs/{id}/",
}

bot = Bot(token=TOKEN)

# All handlers should be attached to the Router (or Dispatcher)
dp = Dispatcher()


def get_related_messages(take_apart_request, chat_id):
    return PermissionRequestTgMessage.objects.filter(
        factory_permission_request=take_apart_request
    ).exclude(chat_id=chat_id)


@dp.callback_query(lambda c: c.data.endswith('_yes') or c.data.endswith('_no'))
async def process_callback_button(callback_query: CallbackQuery):
    callback_data = callback_query.data
    request_id, action = callback_data.split('_')

    try:
        take_apart_request = await FactoryTakeApartRequest.objects.aget(id=request_id)
    except FactoryTakeApartRequest.DoesNotExist:
        await callback_query.answer("Заявка не найдена.")
        return

    # with transaction.atomic():
    if action == 'yes':
        take_apart_request.is_accepted = True
    elif action == 'no':
        take_apart_request.is_accepted = False

    take_apart_request.is_answered = True

    try:
        product_factory = await ProductFactory.objects.aget(id=take_apart_request.product_factory_id)
    except ProductFactory.DoesNotExist:
        await callback_query.answer("Букет не найден.")
        return

    try:
        if product_factory.status == ProductFactoryStatus.PENDING and take_apart_request.is_accepted:
            response = requests.post(
                url=FACTORY_PERM_API_ENDPOINTS[take_apart_request.request_type].format(
                    url=URL, id=product_factory.id), json={}, auth=HTTPBasicAuth('dev', 'adminadmin')
            )
            response.raise_for_status()
        else:
            product_factory.status = take_apart_request.initial_status
            await product_factory.asave()

    except requests.exceptions.RequestException as e:
        await callback_query.answer("Ошибка при отправке запроса")
        print(e)
        return

    await take_apart_request.asave()

    new_message_text = f"{callback_query.message.text}\n" \
                       f"{'✅ Принято' if take_apart_request.is_accepted else '❌ Отклонено'}\n" \
                       f"Ответил: {callback_query.from_user.full_name}"
    await callback_query.message.edit_reply_markup()
    await callback_query.message.edit_text(
        new_message_text,
        reply_markup=None
    )

    related_messages = PermissionRequestTgMessage.objects.filter(
        factory_permission_request=take_apart_request)
    async for message in related_messages.exclude(chat_id=callback_query.message.chat.id):
        try:
            await bot.edit_message_reply_markup(
                chat_id=message.chat_id, message_id=message.message_id, reply_markup=None)
            await bot.edit_message_text(chat_id=message.chat_id, message_id=message.message_id, text=new_message_text)
        except Exception as e:
            print(e)
    related_messages.adelete()


@dp.callback_query(lambda c: c.data.endswith('_yes2') or c.data.endswith('_no2'))
async def process_callback_button(callback_query: CallbackQuery):
    callback_data = callback_query.data
    request_id, action = callback_data.split('_')

    try:
        permission_request = await ActionPermissionRequest.objects.aget(id=request_id)
    except ActionPermissionRequest.DoesNotExist:
        await callback_query.answer("Заявка не найдена.")
        return

    # with transaction.atomic():
    if action == 'yes2':
        permission_request.is_accepted = True
    elif action == 'no2':
        permission_request.is_accepted = False

    permission_request.is_answered = True

    if permission_request.request_type == ActionPermissionRequestType.PRODUCT_WRITE_OFF:
        write_off_obj: WarehouseProductWriteOff = await WarehouseProductWriteOff.objects.aget(
            id=permission_request.wh_product_write_off_id)

        try:
            if not write_off_obj.is_deleted and not permission_request.is_accepted:
                response = requests.delete(
                    url=GENERAL_PERM_API_ENDPOINTS[permission_request.request_type].format(
                        url=URL, id=write_off_obj.id), json={}, auth=HTTPBasicAuth('dev', 'adminadmin')
                )
                response.raise_for_status()

        except requests.exceptions.RequestException as e:
            await callback_query.answer("Ошибка при отправке запроса")
            print(e)
            return

    await permission_request.asave()

    new_message_text = f"{callback_query.message.text}\n" \
                       f"{'✅ Принято' if permission_request.is_accepted else '❌ Отклонено'}\n" \
                       f"Ответил: {callback_query.from_user.full_name}"
    await callback_query.message.edit_reply_markup()
    await callback_query.message.edit_text(
        new_message_text,
        reply_markup=None
    )
    related_messages = PermissionRequestTgMessage.objects.filter(
        action_permission_request=permission_request)
    async for message in related_messages.exclude(chat_id=callback_query.message.chat.id):
        try:
            await bot.edit_message_reply_markup(
                chat_id=message.chat_id, message_id=message.message_id, reply_markup=None)
            await bot.edit_message_text(chat_id=message.chat_id, message_id=message.message_id, text=new_message_text)
        except Exception as e:
            print(e)
    related_messages.adelete()


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await message.answer("Бот активирован")


async def main():
    # await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    asyncio.run(main())
