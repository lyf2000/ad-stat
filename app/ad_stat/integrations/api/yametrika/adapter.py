from typing import Any

from apps.users.models.oauth import YandexProfile
from damri.integrations.api.yametrika.adapter import (
    YaMetrikaManagementAdapterAPIClient as DamriYaMetrikaManagementAdapterAPIClient,
)


class YaMetrikaManagementAdapterAPIClient(DamriYaMetrikaManagementAdapterAPIClient):
    def _get_tokens(self) -> list[Any]:
        return list(YandexProfile.objects.all().values_list("token", flat=True))
