from ad_stat.integrations.api.yandex.api import YandexAPIClient
from common.collectors import BaseDataCollector
from damri.integrations.api.yametrika.models import UserModel


class YandexDataCollector(BaseDataCollector):
    def __init__(self, token: str) -> None:
        super().__init__()
        self.token = token
        self.client = YandexAPIClient(self.token)

    def myself(self) -> UserModel:
        """
        Информация о текущем пользователе.
        """
        return self.client.myself()
