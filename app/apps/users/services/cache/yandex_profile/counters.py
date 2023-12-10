from ad_stat.integrations.api.yametrika.adapter import (
    YaMetrikaManagementAdapterAPIClient,
)
from ad_stat.integrations.api.yametrika.models import CounterModel
from apps.users.models.oauth import YandexProfile
from apps.users.services.cache.yandex_profile.base import BaseYandexProfileDataCache
from common.cache import BaseDataDetailCacheCollector
from common.models import BaseModel
from pydantic import Field


class CounterData(CounterModel):
    pass


class YanderProfileData(BaseModel):
    counters: list[CounterData] = Field(default_factory=list)


class _YandexPRofileCountersDetailDataCache(BaseDataDetailCacheCollector):
    """
    Список плательщиков.
    """

    PREFIX = BaseYandexProfileDataCache.PREFIX
    KEY_TEMPLATE = PREFIX + ".counters.{0}"
    ITEM_CLASS = YanderProfileData
    TIMEOUT = 86400  # 1d TODO: add enum

    def get_key(self, id: YandexProfile):
        return self.KEY_TEMPLATE.format(id.id)

    def _collet_data(self, id: YandexProfile) -> YanderProfileData:
        return self.ITEM_CLASS(
            counters=[
                CounterData(**counter_data.dict())
                for counter_data in YaMetrikaManagementAdapterAPIClient(tokens=[id.token]).all().counters()
            ]
        )


YandexPRofileCountersDetailDataCache = _YandexPRofileCountersDetailDataCache()
