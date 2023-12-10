import logging

from ad_stat.integrations.api.click_ru.api import ClickRuAPIClient
from apps.users.models.oauth import YandexProfile
from apps.users.services.cache.yandex_profile.manager import (
    YandexProfileDataCacheManager,
)
from common.collectors import BaseDataCollector

logger = logging.getLogger(__name__)


# TODO mv all cache managers here
class YandexProfileDataCollector(BaseDataCollector):
    def __init__(self, user_id: int) -> None:
        super().__init__()
        self.user_id = user_id
        self.api_client = ClickRuAPIClient(user_id=self.user_id)

    @classmethod
    def get_counter_yandex_profile(cls, counter_id: int) -> YandexProfile:
        try:
            return next(
                profile
                for profile in YandexProfile.objects.all()
                if counter_id
                in [
                    counter.id
                    for counter in YandexProfileDataCacheManager.get_yandex_profile_counters(profile)
                ]
            )
        except StopIteration as err:
            logger.error(f"No yandex profile found for counter_id: {counter_id}")
            raise err
