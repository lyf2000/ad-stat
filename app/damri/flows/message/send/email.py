from damri.flows.message.send.base import BaseMessageSendFlow
from damri.services.message.sender.email import EmailSenderService


class SendEmailFlow(BaseMessageSendFlow):
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
        return []

    def _pre_exec(self, *args, **kwargs):
        self._title = self._get_title()
        self._body = self._get_body()
        self._to = self._get_send_to()
        self._attachements = self._get_attachements()

    def _send(self):
        EmailSenderService(self._to, self.title, self.body, attachements=self._attachements).send()
