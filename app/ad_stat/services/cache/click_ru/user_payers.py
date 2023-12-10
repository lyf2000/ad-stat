from ad_stat.integrations.api.click_ru.api import ClickRuAPIClient
from ad_stat.integrations.api.click_ru.models import PayerModel as PayerModel_
from ad_stat.services.cache.click_ru.base import BaseClickRuDataCache
from common.cache import BaseDataDetailCacheCollector
from common.models import BaseModel
from pydantic import Extra, Field


class PayerModel(PayerModel_):
    pass


class UserPayersData(BaseModel, extra=Extra.allow):
    payers: list[PayerModel] = Field(default_factory=list)


class _UserPayersDetailDataCache(BaseDataDetailCacheCollector):
    """
    Список плательщиков.
    """

    PREFIX = BaseClickRuDataCache.PREFIX
    KEY_TEMPLATE = PREFIX + ".payers.{0}"
    ITEM_CLASS = UserPayersData
    TIMEOUT = 3600  # 1h TODO: add enum

    def _collet_data(self, id) -> UserPayersData:
        return self.ITEM_CLASS(
            payers=[PayerModel(**payer.dict()) for payer in ClickRuAPIClient(user_id=id).payers()]
        )


UserPayersDetailDataCache = _UserPayersDetailDataCache()
