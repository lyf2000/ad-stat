from apps.users.services.collectors.yandex_profile import YandexProfileDataCollector
from damri.collectors.yametrika.counter_stats import (
    CounterStatsDataCollector as DamriCounterStatsDataCollector,
)


class CounterStatsDataCollector(DamriCounterStatsDataCollector):
    def _get_token(self) -> str:
        return YandexProfileDataCollector.get_counter_yandex_profile(self.counter_id).token
