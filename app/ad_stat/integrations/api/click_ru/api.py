import os
from datetime import date
from io import BytesIO
from typing import List

from ad_stat.integrations.api.base import (
    BaseRequestsClient,
    CSVResponseParser,
    SourceResponseParser,
    request,
)
from ad_stat.integrations.api.click_ru.models import (
    AccountModel,
    CampaignModel,
    InvoiceModel,
    MasterUserModel,
    PayerModel,
    StatModel,
    UserModel,
)


class ClickRuAPIClient(BaseRequestsClient):
    domain = "https://api.click.ru/V0/"
    _headers = {
        "X-Auth-Token": os.getenv("MASTER_TOKEN"),  # master's token
    }

    def __init__(self, user_id: int):
        self.user_id = str(user_id)

    @property
    def headers(self):
        return {**super().headers, "X-Auth-UserId": self.user_id}

    @request(response_model=StatModel, response_parser=CSVResponseParser())
    def stat(self, start_date: date, end_date: date) -> List[StatModel]:
        url = "stat?fields=accountId,campaignId,date,impressions,clicks,loss&dateFrom={start_date}&dateTo={end_date}&includeHeaders=true".format(
            start_date=start_date.strftime("%Y-%m-%d"), end_date=end_date.strftime("%Y-%m-%d")
        )

        return self.get(url)

    @request(response_model=AccountModel, response_parser=SourceResponseParser("response.accounts"))
    def accounts(self) -> List[AccountModel]:
        url = "accounts"

        return self.get(url)

    @request(response_model=AccountModel, response_parser=SourceResponseParser("response.accounts"))
    def account(self, id) -> AccountModel:
        url = f"accounts/{id}"

        return self.get(url)

    @request(response_model=CampaignModel, response_parser=SourceResponseParser("response.items"))
    def campaigns(self) -> List[CampaignModel]:
        url = "campaigns?showDeleted=true"

        return self.get(url)

    @request(response_model=UserModel, response_parser=SourceResponseParser("response"))
    def user(self) -> UserModel:
        url = "user"

        return self.get(url)

    @request(response_model=InvoiceModel, response_parser=SourceResponseParser("response"))
    def create_payment_invoice(self, payer_id: int, amount: float) -> InvoiceModel:
        url = "payments/invoices"

        data = dict(payerId=payer_id, amount=amount)
        return self.post(url, data=data)

    def get_invoice_pdf(self, invoice_id: int) -> BytesIO:
        url = f"payments/invoices/{invoice_id}.pdf"

        with self._download_file(url) as file:
            return file

    @request(response_model=PayerModel, response_parser=SourceResponseParser("response.payers"))
    def payers(self) -> list[PayerModel]:
        url = "users/payers"

        return self.get(url)


class ClickRuMasterAPIClient(ClickRuAPIClient):
    _headers = {
        "X-Auth-Token": os.getenv("MASTER_TOKEN"),  # master's token
    }

    def __init__(self):
        pass

    @property
    def headers(self):
        return self._headers

    @request(response_model=MasterUserModel, response_parser=SourceResponseParser("response.users"))
    def users(self) -> list[MasterUserModel]:
        url = "users"

        return self.get(url)
