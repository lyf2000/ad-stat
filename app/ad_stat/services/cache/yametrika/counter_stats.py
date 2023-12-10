from ad_stat.integrations.api.yametrika.models import CounterStatModel
from ad_stat.services.cache.yametrika.base import BaseYaMetrikaDataCache
from ad_stat.services.collectors.ya_metrika.counter_stats import (
    CounterStatsDataCollector,
)
from common.cache import BaseDataDetailCacheCollector
from common.models import BaseModel
from pydantic import Field


class CounterStatData(CounterStatModel):
    pass


class CounterStatsData(BaseModel):
    stats: list[CounterStatData] = Field(default_factory=list)


class _CounterStatsDataDetailCacheCollector(BaseDataDetailCacheCollector):
    PREFIX = BaseYaMetrikaDataCache.PREFIX
    KEY_TEMPLATE = PREFIX + ".counter-stats.{0}"
    ITEM_CLASS = CounterStatsData
    TIMEOUT = 60  # 1 min TODO

    def _collet_data(self, id: int) -> CounterStatsData:
        return self.ITEM_CLASS(
            stats=[
                CounterStatData(**account.dict())
                for account in CounterStatsDataCollector(counter_id=id).stats_yesterday()
            ]
        )


CounterStatsDataDetailCacheCollector = _CounterStatsDataDetailCacheCollector()
