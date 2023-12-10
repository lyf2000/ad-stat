from decimal import Decimal

from ad_stat.choices import WeekDayChoices
from ad_stat.integrations.api.click_ru.api import ClickRuAPIClient
from ad_stat.models.company import Company
from ad_stat.services.cache.click_ru.base import BaseClickRuDataCache
from common.models import BaseModel
from damri.collectors.cache import BaseDataKeysCacheCollectorV2
from damri.services.tasks.cache.base import BaseCacheTaskService


class CompanyWeekDayBalanceUserData(BaseModel):
    login_balances: dict[str, Decimal]
    balance: Decimal


class WeekDayClickRUBalanceDataCache(BaseDataKeysCacheCollectorV2):
    PREFIX = BaseClickRuDataCache.PREFIX
    KEY_TEMPLATE = PREFIX + ".weekday-balance.{id}.{weekday}"
    ITEM_CLASS = CompanyWeekDayBalanceUserData
    TIMEOUT = 60 * 60 * 24 * 7 - 1  # 7 days
    AUTO_COLLECT = False

    def __init__(self, weekday: type[WeekDayChoices], company: Company) -> None:
        super().__init__()
        self.company = company
        self.weekday = weekday

    def get_keys_init(self) -> dict:
        return dict(
            id=self.company.pk,
            weekday=self.weekday,
        )

    def _collet_data(self) -> CompanyWeekDayBalanceUserData:
        accounts = ClickRuAPIClient(self.company.click_ru_user_id).accounts()
        profiles = {account.serviceLogin: Decimal(account.balance) for account in accounts}

        return self.ITEM_CLASS(
            login_balances=profiles,
            balance=ClickRuAPIClient(self.company.click_ru_user_id).user().balance,
        )


class WeekDayClickRuBalanceCacheTaskCollector(BaseCacheTaskService):
    CACHE_SERVICE = WeekDayClickRUBalanceDataCache

    def __init__(self, weekday: type[WeekDayChoices]) -> None:
        super().__init__()
        self.weekday = weekday

    def _collect(self):
        for company in Company.objects.click_ru():
            WeekDayClickRUBalanceDataCache(weekday=self.weekday, company=company).set_data()
