from typing import Any

from ad_stat.choices import NotieLogTypes
from common.services.tg_bot import TgBotMessageSenderService
from flows.bots.base import BaseBotFlow


class _TgBotSendFlow(BaseBotFlow):
    STAT_TYPE = NotieLogTypes

    def _exec(self, msgs: list[str], to: list[int] | None = None, to_admin=False) -> Any:
        if not msgs:
            raise ValueError("No messages to send")

        if to is None and not to_admin:
            raise ValueError("Not selected to chats or to admin")

        if to_admin:
            TgBotMessageSenderService(msgs).send_msg_admin()
            return

        self.result = TgBotMessageSenderService(chat_ids=to, msgs=msgs).send_msg_chats()

    def _post_exec(self, *args, **kwargs) -> Any:
        return self.result


TgBotSendFlow = _TgBotSendFlow()
