import logging
import os

from aiogram import Bot, Dispatcher
from aiogram.types import MenuButtonCommands

from .handlers import my_router

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

TOKEN = os.getenv("BOT_TOKEN")


async def on_startup(bot: Bot):
    await bot.set_chat_menu_button(menu_button=MenuButtonCommands(text="menu"))


# # TODO mv to class
# @dispatcher.message_handler(Command("start"))
# async def send_welcome(message: types.Message):
#     await message.answer(f"ID чата: `{message.chat.id}`", parse_mode=ParseMode.MARKDOWN)


# @dispatcher.message_handler(commands=["invoice"])
# async def start_send_invoice(message: types.Message):
#     await message.answer(f"ID чата: `{message.chat.id}`", parse_mode=ParseMode.MARKDOWN)


# # @dp.message_handler(commands=["invoice"])
# async def handle_send_invoice(message: types.Message):
#     await message.answer(f"ID чата: `{message.chat.id}`", parse_mode=ParseMode.MARKDOWN)


async def main():
    bot = Bot(token=TOKEN)
    dp = Dispatcher()
    dp.startup.register(on_startup)

    dp.include_router(my_router)

    await dp.start_polling(bot)
