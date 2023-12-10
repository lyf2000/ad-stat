
from ad_stat.integrations.api.base import BaseRequestsClient, request
from ad_stat.integrations.api.yandex.models import UserModel


class YandexAPIClient(BaseRequestsClient):
    domain = "https://login.yandex.ru/"

    def __init__(self, token: str):
        self.token = token

    @property
    def headers(self):
        return {"Authorization": f"Bearer {self.token}"}

    @request(response_model=UserModel)
    def myself(self) -> UserModel:
        url = "info"

        return self.get(url)
