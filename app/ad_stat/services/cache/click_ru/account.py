from ad_stat.services.cache.click_ru.base import BaseClickRuDataCache
from ad_stat.services.noties.click_ru.collector import (
    CampaignsStatDataCollectorAPIService,
)
from common.cache import BaseDataDetailCacheCollector
from common.models import BaseModel
from common.utils import WordToDateParser
from pydantic import Extra, Field


class ActiveAccountsData(BaseModel, extra=Extra.allow):
    account_ids: list = Field(default_factory=list)


class _DynamicActiveAccountsDetailDataCache(BaseDataDetailCacheCollector):
    """Список активных аккаунтов.

    Активность определяется наличием ненулевых полей `clicks`.
    """

    PREFIX = BaseClickRuDataCache.PREFIX
    KEY_TEMPLATE = PREFIX + ".account.dynamic-active.{0}"
    ITEM_CLASS = ActiveAccountsData
    TIMEOUT = 60  # 1h TODO: add enum

    def _collet_data(self, id) -> ActiveAccountsData:
        return self.ITEM_CLASS(
            account_ids=[
                stat_grouped.accountId
                for stat_grouped in CampaignsStatDataCollectorAPIService(
                    start_date=WordToDateParser(previous_n_day=30),
                    user_id=id,
                ).get_stat_grouped_by_accounts()
                if stat_grouped.impressions > 0
            ]
        )


DynamicActiveAccountsDetailDataCache = _DynamicActiveAccountsDetailDataCache()
