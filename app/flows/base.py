from typing import Any

from ad_stat.services.email.send import EmailSenderService
from common.mixins import ContextMixin


class BaseBusinessFlow(ContextMixin):
    """
    Базовый класс флоу бизнес логики.
    """

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        """
        Исполнить логику.
        """
        self._pre_exec(*args, **kwargs)
        result = self._exec(*args, **kwargs)
        self._post_exec(*args, **kwargs)
        return result

    def _exec(self, *args, **kwargs):
        """
        Исполнение логики.
        """

    def _pre_exec(self, *args, **kwargs):
        """
        Преподготовка до самого исполнения.
        """

    def _post_exec(self, *args, **kwargs) -> Any:
        """
        Доплогика после исполнения основной.
        """


class SendEmailFlow(BaseBusinessFlow):
    TITLE = ""
    BODY = ""

    @property
    def title(self):
        return self._title

    @property
    def body(self):
        return self._body

    def _get_title(self):
        return self.TITLE

    def _get_body(self):
        return self.BODY

    def _get_send_to(self):
        raise NotImplementedError

    def _get_attachements(self):
        raise None

    def _pre_exec(self, *args, **kwargs):
        self._title = self._get_title()
        self._body = self._get_body()
        self._to = self._get_send_to()
        self._attachements = self._get_attachements()

    def _exec(self):
        self._send()

    def _send(self):
        EmailSenderService(self._to, self.title, self.body, attachements=self._attachements).send()
