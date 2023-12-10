from typing import Any


class Types:
    class EmptyMessages:
        pass


class BaseMessageSenderService:
    def send(self, to: list[Any], msgs: list[str]):
        raise NotImplementedError
