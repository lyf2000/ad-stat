from damri.flows.base import BaseBusinessFlow
from damri.flows.message.deliver.model import MessageModelMixin


class BaseMessageModelDeliverFlow(BaseBusinessFlow):
    MESSAGE_MODEL: MessageModelMixin = None

    def __init__(self, message_sender):
        self.message_sender = message_sender
        self.message = None
        self.send_status_data = None
        self.result = None

    def _exec(self):
        self.send_status_data = self.message_sender.send()

    def _pre_exec(self):
        raise NotImplementedError

    def _post_exec(self):
        return self.message
