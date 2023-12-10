from datetime import date
from typing import List

from ad_stat.integrations.api.click_ru.api import ClickRuAPIClient
from ad_stat.integrations.api.click_ru.models import (
    AccountModel,
    CampaignModel,
    StatModel,
    UserModel,
)
from common.services import BaseDataCollectorAPIService
from django.utils.timezone import now


class CampaignsStatDataCollectorAPIService(BaseDataCollectorAPIService):
    def __init__(self, start_date: date, user_id: int, end_date: date | None = None) -> None:
        super().__init__()
        self.start_date = start_date
        self.end_date = end_date or now().date()
        self.user_id = user_id
        self.client = ClickRuAPIClient(self.user_id)

    def get_accounts(self) -> List[AccountModel]:
        """
        Список аккаунтов.
        """
        return self.client.accounts()

    def get_campaigns(self) -> List[CampaignModel]:
        """
        Список кампаний аккаунта.
        """
        return self.client.campaigns()

    def get_stat(self) -> List[StatModel]:
        """
        Статистика по кампаниям.
        """
        return self.client.stat(start_date=self.start_date, end_date=self.end_date)

    def get_stat_grouped_by_campaigns(self) -> List[StatModel]:
        """
        Статистика по кампаниям с группировкой по кампаниям.
        """
        stats = self.get_stat()

        return StatModel.grouped_by_campaigns(stats)

    def get_stat_grouped_by_accounts(self) -> List[StatModel]:
        """
        Статистика по аккаунтам с группировкой по аккаунтам.
        """
        stats = self.get_stat()

        return StatModel.grouped_by_account(stats)

    def get_user(self) -> UserModel:
        """
        Пользователь.
        """
        return self.client.user()
