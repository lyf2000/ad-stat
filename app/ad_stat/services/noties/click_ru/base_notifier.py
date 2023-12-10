from collections import Counter, defaultdict
from datetime import date
from decimal import Decimal
from enum import Enum

from ad_stat.integrations.api.click_ru.models import (
    AccountModel,
    CampaignModel,
    StatModel,
    UserModel,
)
from ad_stat.models import Company
from ad_stat.services.collectors.click_ru import AccountData
from ad_stat.services.noties.click_ru.collector import (
    CampaignsStatDataCollectorAPIService,
)
from common.services.base import BaseNotifierMessageBuilderService
from common.utils import repr_number, with_nds


class ServiceEnum(Enum):
    DIRECT = "Yandex.ru"
    ADWORDS = "Google.com"
    YMAPS = "Yandex.ru"
    FB = "Facebook.com"
    AVITO = "Avito.ru"
    VK = "Vk.com"
    VK_ADS = "Vk.com"


class CoreClickRuNotifierMessageBuilderService(BaseNotifierMessageBuilderService):
    def get_site_url(self, company: Company, named=False) -> str:
        if not company.site_url:
            return "Не указано"

        link = company.site_url
        if named:
            return self.get_named_link(company.name, link)
        return link

    @staticmethod
    @repr_number
    def get_account_balance(account: AccountModel) -> int | Decimal | float:
        return with_nds(account.balance)  # нужен НДС

    @staticmethod
    def repr_account(account: AccountData, accounts: list[AccountData]) -> str:
        """
        Отобржение имени счета.

        Если счетов по компании больше 1, то выводим
        имя компании + счета, иначе имя компании.

        Args:
            account (AccountData): _description_
            accounts (list[AccountData]): _description_

        Returns:
            str: _description_
        """
        return (
            f"{account.company.name}. {account.name}"
            if Counter(account_.company.id for account_ in accounts)[account.company.id] > 1
            else account.company.name
        )

    def tag_company_tg_responsible(self, company: Company) -> str:
        return (
            self.tag_user(company.responsible.tg_username)
            if company.responsible.tg_username
            else company.responsible.name
        )


class BaseStatNotifierMessageBuilderService(CoreClickRuNotifierMessageBuilderService):
    COLLECT_CLICK_RU = True

    def __init__(self, start_date: date, end_date: date, company: Company) -> None:
        super().__init__()
        self.start_date = start_date
        self.end_date = end_date
        self.company = company

        if self.COLLECT_CLICK_RU:
            self.collector = CampaignsStatDataCollectorAPIService(
                start_date=self.start_date, end_date=self.end_date, user_id=self.company.click_ru_user_id
            )
            (
                self.stats,
                self.accounts,
                self.user,
                self.accounts_map,
                self.campaigns_map,
                self.account_stats,
            ) = self.get_base_data()

            self.selected_accounts = (
                [account for account in self.accounts if account.serviceLogin in self.company.yandex_account_logins]
                if self.company.yandex_account_logins
                else []
            )
            # only if selected accounts
            if self.selected_accounts:
                self.account_stats = {
                    account: stats for account, stats in self.account_stats.items() if account in self.selected_accounts
                }

    def get_site_url(self) -> str:
        return super().get_site_url(self.company)

    def get_base_data(
        self,
    ) -> tuple[
        list[StatModel],
        list[AccountModel],
        UserModel,
        dict[int, AccountModel],
        dict[int, CampaignModel],
        dict[AccountModel, list[StatModel]],
    ]:
        stats, accounts, user = self.get_stat_data(), self.collector.get_accounts(), self.collector.get_user()

        accounts_map: dict[int, AccountModel] = {account_.id: account_ for account_ in accounts}
        campaigns_map: dict[int, CampaignModel] = {
            campaign_.id: campaign_ for campaign_ in self.collector.get_campaigns()
        }

        account_stats: dict[AccountModel, list[StatModel]] = defaultdict(lambda: list())
        [account_stats[accounts_map[stat.accountId]].append(stat) for stat in stats]

        return stats, accounts, user, accounts_map, campaigns_map, account_stats

    def get_stat_data(self) -> list[StatModel]:
        return self.collector.get_stat()

    @staticmethod
    @repr_number
    def get_balance(user: UserModel) -> str:
        return abs(user.balance)

    @staticmethod
    def get_campaign_name(campaign: CampaignModel) -> str:
        return campaign.name

    @staticmethod
    @repr_number
    def get_account_loss(stats: list[StatModel]) -> float:
        return sum(stat.loss for stat in stats)

    @classmethod
    @repr_number
    def get_company_loss(cls, account_stats: dict[AccountModel, list[StatModel]]) -> float:
        return cls.get_company_loss_(account_stats)

    @classmethod
    def get_company_loss_(cls, account_stats: dict[AccountModel, list[StatModel]]) -> float:
        return sum(cls.get_account_loss._original(stats) for stats in account_stats.values())  # нужен НДС
