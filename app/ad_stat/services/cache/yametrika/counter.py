from ad_stat.integrations.api.yametrika.adapter import (
    YaMetrikaManagementAdapterAPIClient,
)
from ad_stat.integrations.api.yametrika.models import CounterModel
from ad_stat.services.cache.yametrika.base import BaseYaMetrikaDataCache
from common.models import BaseModel
from pydantic import Field


class CounterData(CounterModel):
    pass


class CountersData(BaseModel):
    counters: list[CounterData] = Field(default_factory=list)


class _AllYaMetrikaCountersDataCache(BaseYaMetrikaDataCache):
    KEY = "counters"
    ITEM_CLASS = CountersData
    TIMEOUT = 1  # TODO move to zero

    def _collet_data(self) -> CountersData:
        return self.ITEM_CLASS(
            counters=[
                CounterData(**counter_data.dict())
                for counter_data in YaMetrikaManagementAdapterAPIClient().all().counters()
            ]
        )


AllYaMetrikaCountersDataCache = _AllYaMetrikaCountersDataCache()
