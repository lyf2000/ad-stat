from dataclasses import dataclass, field
from io import BytesIO
from typing import Type

from bots.telegram.aiogramm.utils import split_text
from common.services.message_sender import BaseMessageSenderService
from common.services.tg_bot import TgBotMessageSenderService, TgMessageItem
from telegram.message import escape_markdown


class BaseService:
    pass


class BaseDataCollector(BaseService):
    pass


# TODO need?
class BaseDataCollectorAPIService(BaseService):
    pass


class BaseNotifierService(BaseService):
    def __init__(self) -> None:
        self.message_sender: Type[BaseMessageSenderService] = None

    def send_noties_channels(self) -> None:
        self._send_noties_channels()

    def _send_noties_channels(self) -> None:
        raise NotImplementedError

    def send_notie(self) -> None:
        self._send_notie()

    def _send_notie(self) -> None:
        raise NotImplementedError


class BaseTgNotifierService(BaseNotifierService):
    def __init__(self) -> None:
        self.message_sender = TgBotMessageSenderService


@dataclass
class TgMessage:
    heading: TgMessageItem
    items: list[TgMessageItem] = field(default_factory=list)


class TgMessageBuilderServiceMixin:
    def get_named_link(self, link: str, name: str) -> str:
        return f"[{name}]({link})"

    def attach_file(self, msg: TgMessageItem, file: BytesIO, name: str) -> None:
        msg.attachments.append((file, name))

    @classmethod
    def compose_msgs(cls, messages: list[TgMessage], separate=False) -> list[TgMessageItem]:
        composed = []
        for counter, message in enumerate(messages):
            if not separate:
                if counter == 0:
                    msg_item = messages[0].heading
            else:
                msg_item = message.heading

            items = message.items
            if counter > 0 and not separate:
                items = [message.heading, *items]

            for item in items:
                msgs = cls.merge_msgs(message.heading.msg, msg_item.msg, item.msg)
                msg_item.msg = msgs[0]
                if len(msgs) > 1:
                    msg_item.attachments.extend(item.attachments)
                    msg_item.msg = msgs[0]
                    composed.append(msg_item)
                    msg_item = TgMessageItem(msgs[1], item.attachments)
            if separate:
                composed.append(msg_item)

        if not separate:
            composed.append(msg_item)
        return composed

    @classmethod
    def merge_msgs(cls, head: str, msg_1: str, msg_2: str) -> list[str]:
        if len(split_text(msg_1 + msg_2)) > 1:
            return [msg_1, f"{head}{msg_2}"]

        return [f"{msg_1}{msg_2}"]

    @staticmethod
    def tag_user(tag: str) -> str:
        return escape_markdown(tag, version=1)


class BaseNotifierMessageBuilderService(TgMessageBuilderServiceMixin, BaseService):
    def compose_msg(self, separated=False, separated_all=False) -> list[str]:
        return self._process_composed_msgs(self.get_head_msg(), separated, separated_all, self.get_item_msgs())

    def _process_composed_msgs(
        self, head: str | TgMessageItem | None, separated, separated_all, items: list[str | TgMessageItem] | None
    ) -> list[str]:
        if items is not None and len(items) == 0 or head is None:
            return []

        tg_item = type(head) is TgMessageItem
        msgs = []
        msg = head
        if tg_item:
            msg = ""
            msgs.append(head)
        if items:
            for counter, item in enumerate(items):
                if type(item) is TgMessageItem:
                    if counter == 0 and type(head) is str:
                        item.msg = "".join([head, item.msg])
                        msg = ""
                    msgs.append(item)
                elif separated_all or separated and counter != 0:
                    msgs.append(item)
                elif separated and counter == 0 or not separated:
                    if len(split_text(msg + item)) > 1:
                        msgs.append(msg)
                        msg = item
                    else:
                        msg += item

        if msg:
            return [*msgs, msg]
        else:
            return msgs

    def get_item_msgs(self) -> list[str | TgMessageItem] | None:
        return None

    def get_head_msg(self) -> str | TgMessageItem | None:
        raise NotImplementedError
