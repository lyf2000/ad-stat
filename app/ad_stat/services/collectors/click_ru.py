from io import BytesIO

from ad_stat.integrations.api.click_ru.api import ClickRuAPIClient
from ad_stat.integrations.api.click_ru.models import PayerTypeEnum
from ad_stat.services.cache.click_ru.manager import ClickRuDataCacheManager
from ad_stat.services.cache.click_ru.user_payers import PayerModel
from common.collectors import BaseDataCollector
from common.models import BaseModel
from pydantic import Extra, Field


class AccountData(BaseModel, extra=Extra.allow):
    id: int
    name: str
    balance: float
    service: str
    serviceLogin: str


class UserData(BaseModel):
    id: int
    accounts: list[AccountData] = Field(default_factory=list)


# TODO mv all cache managers here
class ClickRuDataCollector(BaseDataCollector):
    def __init__(self, user_id: int) -> None:
        super().__init__()
        self.user_id = user_id
        self.api_client = ClickRuAPIClient(user_id=self.user_id)

    def user_accounts_data(self) -> UserData:
        return UserData(
            id=self.user_id,
            accounts=[
                AccountData(
                    id=account.id,
                    balance=account.balance,
                    service=account.service,
                    name=account.name,
                    serviceLogin=account.serviceLogin,
                )
                for account in ClickRuAPIClient(user_id=self.user_id).accounts()
            ],
        )

    def payers(self) -> list[PayerModel]:
        """
        Список плательщиков.
        """

        return [
            payer
            for payer in ClickRuDataCacheManager.company_payers(self.user_id)
            if payer.type in [PayerTypeEnum.BUSINESS, PayerTypeEnum.INDIVIDUAL]
        ]

    def invoice_pdf(self, invoice_id: int) -> BytesIO:
        """
        ПДФ-файл безналичного счета.
        """

        return self.api_client.get_invoice_pdf(invoice_id)

    @classmethod
    def get_tg_id_click_ru_user_id(cls, tg_id) -> int | None:
        """
        Получение id из клика у компании.

        Args:
            tg_id (int): _description_
        """
        return ClickRuDataCacheManager.get_tg_id_company_data(tg_id).click_ru_user_id
