from ad_stat.services.cache.yametrika.counter import (
    AllYaMetrikaCountersDataCache,
    CounterData,
)


class _YaMetrikaDataCacheManager:
    def get_counters(self) -> list[CounterData]:
        return AllYaMetrikaCountersDataCache.get().counters


YaMetrikaDataCacheManager = _YaMetrikaDataCacheManager()
