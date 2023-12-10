from damri.services.base import BaseService


class BaseMessageSenderService(BaseService):
    def send(self):
        self._send()

    def _send(self):
        raise NotImplementedError
