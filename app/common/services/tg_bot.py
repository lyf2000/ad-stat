import logging
import os
from asyncio import sleep
from io import BytesIO

from aiogram import Bot
from aiogram.enums import ParseMode
from aiogram.types import BufferedInputFile, InputMediaAudio
from asgiref.sync import async_to_sync
from common.services.message_sender import BaseMessageSenderService, Types
from constance import config
from damri.utils.list import chunker

logger = logging.getLogger(__name__)


class TgMessageItem:
    def __init__(self, msg: str, attachments: list[tuple[bytes | BytesIO, str]] | None = None):
        self.msg = msg
        self.attachments = attachments or []  # (file, name)


class TgBotService:
    def __init__(self) -> None:
        self._bot = Bot(token=os.getenv("BOT_TOKEN"))

    @property
    def bot(self) -> Bot:
        return self._bot

    @async_to_sync
    async def send_msg(self, chat_id: int, msgs: list[str | TgMessageItem]):
        errs = []
        for msg in msgs:
            text = msg
            attachments = None
            if type(msg) is TgMessageItem:
                text = msg.msg
                attachments = msg.attachments

            try:
                if attachments:
                    if len(attachments) == 1:
                        await self.bot.send_document(
                            chat_id,
                            BufferedInputFile((attachments[0][0]), filename=attachments[0][1]),
                            caption=text,
                            parse_mode=ParseMode.MARKDOWN,
                        )
                    else:
                        await self.bot.send_message(
                            chat_id, text, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True
                        )
                        # TODO decompose
                        for part in chunker(attachments, 10):
                            media = [
                                InputMediaAudio(media=BufferedInputFile(attachment[0], filename=attachment[1]))
                                for attachment in part
                            ]
                            sent = False
                            while not sent:
                                try:
                                    await self.bot.send_media_group(chat_id, media=media)
                                except:
                                    await sleep(5)
                                    continue
                                sent = True
                else:
                    await self.bot.send_message(
                        chat_id, text, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True
                    )
            except Exception as err:
                logger.warn(f"Error during sending message to telegram channel {chat_id}\n{err}")
                errs.append(f"chat {chat_id}: {err}")

        return errs or None


class TgBotMessageSenderService(BaseMessageSenderService):
    ADMIN_CHATS = [config.ADMIN_TG_ID]

    def __init__(self, msgs: list[str], chat_ids: list[int] | None = None):
        self._bot_service = TgBotService()
        self.msgs = msgs
        self.chat_ids = list(set(chat_ids)) if chat_ids is not None else []

    def send(self):
        errs = self._send_msg_chats()

        if errs is Types.EmptyMessages:
            logger.info(f"No messages to send to {self.chat_ids}")
        elif errs:
            logger.info(f"error sending to {self.chat_ids}\n{errs}")
        else:
            logger.info(f"message{'s' if len(self.msgs) > 1 else ''} sent to {self.chat_ids}")

        return errs

    def _send_msg_chats(self):  # TODO: move to celery
        if not self.msgs:
            return Types.EmptyMessages

        errs = []
        for chat_id in self.chat_ids:
            err = self._bot_service.send_msg(chat_id, self.msgs)
            if err:
                errs.append(err)

        return errs or False

    def send_msg_chats(self):  # TODO: move to celery
        return self.send()

    def send_msg_admin(self):  # TODO: move to celery
        self.chat_ids = self.ADMIN_CHATS
        return self.send()
