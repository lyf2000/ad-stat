import logging

from ad_stat.services.collectors.click_ru import ClickRuDataCollector
from aiogram import Bot, Router
from aiogram.enums import ParseMode
from aiogram.filters.callback_data import CallbackData
from aiogram.filters.command import Command
from aiogram.fsm.middleware import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    BufferedInputFile,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)
from asgiref.sync import sync_to_async
from flows.noties.click_ru.payment_invoice.flow import PaymentInvoiceGenerateFlow

my_router = Router()


@my_router.message(Command(commands=["start"]))
async def command_start(message: Message, bot: Bot):
    # await bot.set_chat_menu_button(
    #     chat_id=message.chat.id,
    #     menu_button=MenuButtonWebApp(
    #         text="Menu",
    #         web_app=WebAppInfo(
    #             url=f"https://stackoverflow.com/questions/68251683/telegram-bot-expandable-menu-at-the-bottom"
    #         ),
    #     ),
    # )

    await message.answer(f"ID чата: `{message.chat.id}`", parse_mode=ParseMode.MARKDOWN)


# @my_router.message(Command(commands=["webview"]))
# async def command_webview(
#     message: Message,
#     base_url: str = "https://stackoverflow.com/questions/68251683/telegram-bot-expandable-menu-at-the-bottom",
# ):
#     await message.answer(
#         "Good. Now you can try to send it via Webview",
#         reply_markup=InlineKeyboardMarkup(
#             inline_keyboard=[
#                 [InlineKeyboardButton(text="Open Webview", web_app=WebAppInfo(url=f"{base_url}"))]
#             ]
#         ),
#     )


# @my_router.message(~F.message.via_bot)  # Echo to all messages except messages via bot
# async def echo_all(
#     message: Message,
#     base_url: str = "https://stackoverflow.com/questions/68251683/telegram-bot-expandable-menu-at-the-bottom",
# ):
#     await message.answer(
#         "Test webview",
#         reply_markup=InlineKeyboardMarkup(
#             inline_keyboard=[[InlineKeyboardButton(text="Open", web_app=WebAppInfo(url=f"{base_url}"))]]
#         ),
#     )

# region choices


class MyCallback(CallbackData, prefix="invoice"):
    selcted_payer_id: int


class InvoiceState(StatesGroup):
    select_payer = State()
    send_amount = State()


# endregion


# region payers invoice create

logger = logging.getLogger("bot.tg.invoice-create")


# def wrap_media(bytesio, **kwargs):
#     """Wraps plain BytesIO objects into InputMediaPhoto"""
#     # First, rewind internal file pointer to the beginning so the contents
#     #  can be read by InputFile class
#     # bytesio.seek(0)
#     return InputMediaPhoto(InputFile(bytesio), **kwargs)


@my_router.message(Command(commands=["invoice"]))
async def start_invoice(message: Message, bot: Bot, state):
    """
    Создание безналичного счета.
    """
    click_ru_id = await sync_to_async(ClickRuDataCollector.get_tg_id_click_ru_user_id)(message.chat.id)
    if click_ru_id is None:
        await message.answer("Не была найдена компания по этому чату или не был задан click.ru id пользователя")
        return

    await state.set_state(InvoiceState.select_payer)
    await state.update_data(click_ru_id=click_ru_id)
    await message.answer(
        "Выберите нужного плательщика",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text=payer.name, callback_data=MyCallback(selcted_payer_id=payer.id).pack())]
                for payer in ClickRuDataCollector(user_id=click_ru_id).payers()
            ]
        ),
    )


@my_router.callback_query(MyCallback.filter())
async def handle_selected_payer(call, bot: Bot, state: FSMContext, callback_data: MyCallback):
    await state.set_state(InvoiceState.send_amount)
    data = await state.get_data()
    await state.update_data(
        selected_payer=next(
            payer
            for payer in ClickRuDataCollector(user_id=data["click_ru_id"]).payers()
            if payer.id == callback_data.selcted_payer_id
        )
    )
    await call.message.answer("Укажите сумму")


@my_router.message(InvoiceState.send_amount)
async def get_payment_link(message: Message, bot: Bot, state: FSMContext, **kwargs):
    try:
        data = await state.get_data()
        click_ru_id, payer, amount = data["click_ru_id"], data["selected_payer"], int(message.text)
        file = PaymentInvoiceGenerateFlow(click_ru_id, payer.id, amount)()

        await message.reply_document(
            BufferedInputFile(file.getbuffer(), filename=f"Счет для {payer.name} на сумму {amount}.pdf")
        )
    # except ClickRuExc:  TODO add err catch
    except ValueError:
        if not message.reply_to_message:
            await state.clear()
            return
        await message.reply_to_message.delete()
        await message.answer("Укажите сумму (только цифры)")
        return
    except Exception as err:
        logger.warn(f"Unhandled err: {err}")
        await message.answer("Ошибка :(")

    await state.clear()


# endregion
