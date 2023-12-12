import os

import requests
from apps.users.models import YandexProfile
from damri.collectors.yametrika.yandex import YandexDataCollector
from flows.base import BaseBusinessFlow


class YandexTokenCreatorFlow(BaseBusinessFlow):
    """
    Процесс генерации токена и сохранения в модель.
    """

    def __init__(self, context: dict | None = None):
        super().__init__(context)

    # TODO add if expired
    def _exec(self, code: str, user: "User", *args, **kwargs):
        # TODO mv to chains
        # chain 1
        url = os.getenv("YAMETRIKA_OAUTH_GET_TOKEN")
        data = dict(
            grant_type="authorization_code",
            client_id=os.getenv("CLIENT_ID"),
            client_secret=os.getenv("CLIENT_SECRET"),
            code=code,
        )
        response = requests.post(url, data)
        response.raise_for_status()
        content = response.json()

        # chain 2
        token = content.pop("access_token")
        data = YandexDataCollector(token).myself().jsonable_dict()

        return token
