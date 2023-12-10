# TODO: add manager
from apps.users.models.oauth import YandexProfile
from apps.users.services.cache.yandex_profile.counters import (
    CounterData,
    YandexPRofileCountersDetailDataCache,
)


class _YandexProfileDataCacheManager:
    def get_yandex_profile_counters(self, yandex_profile: YandexProfile) -> list[CounterData]:
        return YandexPRofileCountersDetailDataCache.get(yandex_profile).counters


YandexProfileDataCacheManager = _YandexProfileDataCacheManager()
