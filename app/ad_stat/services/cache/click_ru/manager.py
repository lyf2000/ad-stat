# TODO: add manager

from decimal import Decimal

from ad_stat.choices import WeekDayChoices
from ad_stat.models.company import Company
from ad_stat.services.cache.click_ru.account import DynamicActiveAccountsDetailDataCache
from ad_stat.services.cache.click_ru.periodic import (
    CompanyWeekDayBalanceUserData,
    WeekDayClickRUBalanceDataCache,
)
from ad_stat.services.cache.click_ru.tg import (
    TgCompanyUserIdTgIdDetailDataCache,
    TgIdData,
)
from ad_stat.services.cache.click_ru.user import MasterUserDataCache, UserData
from ad_stat.services.cache.click_ru.user_payers import (
    PayerModel,
    UserPayersDetailDataCache,
)


class _ClickRuDataCacheManager:
    def get_company_by_id(self, id: int) -> UserData:
        return next(user for user in MasterUserDataCache.get().users if id == user.id)

    def active_account_ids(self, company_id: int):
        return DynamicActiveAccountsDetailDataCache.get(company_id).account_ids

    def company_payers(self, id: int) -> list[PayerModel]:
        return UserPayersDetailDataCache.get(id).payers

    def get_tg_id_company_data(self, id: int) -> TgIdData:
        return TgCompanyUserIdTgIdDetailDataCache.get(id)

    def get_weekday_balances(
        self,
        weekday: type[WeekDayChoices],
        company: Company,
        default=None,
    ) -> CompanyWeekDayBalanceUserData | None:
        return WeekDayClickRUBalanceDataCache(company=company, weekday=weekday).get() or default

    def get_weekday_balance(
        self,
        weekday: type[WeekDayChoices],
        company: Company,
        yandex_login: str | None = None,
        default=None,
    ) -> Decimal | None:
        data = WeekDayClickRUBalanceDataCache(company=company, weekday=weekday).get()
        if not data:
            return default

        if not yandex_login:
            return data.balance

        return data.login_balances[yandex_login]


ClickRuDataCacheManager = _ClickRuDataCacheManager()
