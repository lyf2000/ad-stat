from damri.flows.base import BaseBusinessFlow


class BaseMessageSendFlow(BaseBusinessFlow):
    def _exec(self):
        self._send()

    def _send(self):
        raise NotImplementedError
