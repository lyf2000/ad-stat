import logging

from ad_stat.models.company import Company
from ad_stat.services.cache.click_ru.base import BaseClickRuDataCache
from common.cache import BaseDataDetailCacheCollector
from common.models import BaseModel
from pydantic import Extra


class TgIdData(BaseModel, extra=Extra.allow):
    id: int
    click_ru_user_id: int | None = None


logger = logging.getLogger(__name__)


class _TgCompanyUserIdTgIdDetailDataCache(BaseDataDetailCacheCollector):
    """Список активных аккаунтов.

    Активность определяется наличием ненулевых полей `clicks`.
    """

    PREFIX = BaseClickRuDataCache.PREFIX
    KEY_TEMPLATE = PREFIX + ".tg-id.click-ru-user-id{0}"
    ITEM_CLASS = TgIdData
    TIMEOUT = 3600  # 1h TODO: add enum

    def _collet_data(self, id) -> TgIdData:
        click_ru_user_id = (
            Company.objects.by_telegram_id(id).values_list("click_ru_user_id", flat=True) or None
        )
        if click_ru_user_id:
            if len(click_ru_user_id) > 1:
                logger.warn(f"Found more than 1 companies with telegram_id: {id}")
            click_ru_user_id = click_ru_user_id[0]

        return self.ITEM_CLASS(id=id, click_ru_user_id=click_ru_user_id)


TgCompanyUserIdTgIdDetailDataCache = _TgCompanyUserIdTgIdDetailDataCache()
