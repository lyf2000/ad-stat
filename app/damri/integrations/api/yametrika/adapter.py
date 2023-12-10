from typing import Any, Iterable

from damri.integrations.api.yametrika.api import YaMetrikaManagementAPIClient
from damri.integrations.base.api import BaseAdapterAPIClient


class YaMetrikaManagementAdapterAPIClient(BaseAdapterAPIClient):
    API_CLASS = YaMetrikaManagementAPIClient

    def __init__(self, tokens: list[str] | None = None):
        if tokens is None:
            tokens = self._get_tokens()

        self.tokens = set(tokens)

    def _get_tokens(self) -> list[Any]:
        raise NotImplementedError

    def _per_api_init_data(self) -> Iterable[dict]:
        for token in self.tokens:
            yield dict(token=token)
