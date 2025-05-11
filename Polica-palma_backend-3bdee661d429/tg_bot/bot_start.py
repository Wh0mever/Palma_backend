import asyncio
import os

import django
import requests
from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from asgiref.sync import sync_to_async
from django.db import transaction
from dotenv import load_dotenv

load_dotenv()

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "palma_backend/PalmaCrm.settings")
django.setup()

from src.factory.models import FactoryTakeApartRequest, ProductFactory

from src.factory.enums import ProductFactoryStatus

# Bot token can be obtained via https://t.me/BotFather
# TOKEN = os.environ.get("BOT_TOKEN")
TOKEN = "7534609843:AAGan8Q_blDT_c-nNdC34ky0DG0Eiq4Xzqg"
API_ENDPOINT = "http://localhost:7890/factories/product-factories/{id}/return_to_create/"
# All handlers should be attached to the Router (or Dispatcher)
dp = Dispatcher()


# Async function to get FactoryTakeApartRequest instance by ID
@sync_to_async
def get_factory_take_apart_request(request_id):
    return FactoryTakeApartRequest.objects.get(id=request_id)


# Async function to update the is_accepted field
@sync_to_async
def update_is_accepted(take_apart_request, is_accepted):
    take_apart_request.is_accepted = is_accepted
    take_apart_request.save()


# Callback query handler for inline button clicks
@dp.callback_query(lambda c: c.data.endswith('_yes') or c.data.endswith('_no'))
async def process_callback_button(callback_query: CallbackQuery):
    callback_data = callback_query.data
    request_id, action = callback_data.split('_')

    try:
        take_apart_request = await FactoryTakeApartRequest.objects.aget(id=request_id)
    except FactoryTakeApartRequest.DoesNotExist:
        await callback_query.answer("Заявка не найдена.")
        return

    async with transaction.atomic():
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

        # if product_factory.status == ProductFactoryStatus.FINISHED and take_apart_request.is_accepted:
        #     product_factory.status = ProductFactoryStatus.CREATED
        #     product_factory.finished_at = None
        #     product_factory.finished_user = None
        #     await product_factory.asave()
        #     await sync_to_async(remove_charge_from_product_factory(product_factory))()
        #     await sync_to_async(cancel_product_factory_create_compensation_to_florist(product_factory))()
        try:
            if product_factory.status == ProductFactoryStatus.PENDING and take_apart_request.is_accepted:
                response = requests.post(
                    url=API_ENDPOINT.format(id=product_factory.id), json={}
                )
                response.raise_for_status()
            else:
                product_factory.status = ProductFactoryStatus.FINISHED
                await product_factory.asave()

        except requests.exceptions.RequestException as e:
            await callback_query.answer("Произошла ошибка при отправке запроса.")
            return

        await take_apart_request.asave()

        await callback_query.message.edit_reply_markup()
        await callback_query.message.edit_text(
            f"{callback_query.message.text}\n"
            f"{'✅ Принято' if take_apart_request.is_accepted else '❌ Отклонено'}",
            reply_markup=None
        )


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await message.answer("Погнали нахуй")


async def main():
    bot = Bot(token=TOKEN)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    asyncio.run(main())
