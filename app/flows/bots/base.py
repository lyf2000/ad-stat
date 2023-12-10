from flows.base import BaseBusinessFlow


class BaseBotFlow(BaseBusinessFlow):
    def __init__(self, context: dict|None=None):
        super().__init__(context)

