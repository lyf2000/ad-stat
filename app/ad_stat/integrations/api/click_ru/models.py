from datetime import date as Date
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional

from common.models import BaseFrozenModel, BaseModel
from common.utils import with_nds
from pydantic import Field, validator


class StatModel(BaseModel):
    accountId: int  # какая рекламная компания
    date: Date | None = None
    campaignId: int
    impressions: int
    clicks: int
    loss: Decimal

    @validator("date", pre=True)
    def parse_date(cls, value: str) -> Date:
        return datetime.strptime(value, "%Y-%m-%d").date()

    @validator("loss", pre=True)
    def add_loss_nds(cls, value: str) -> Decimal:
        return with_nds(Decimal(value))

    @classmethod
    def grouped_by_campaigns(cls, stats: list["StatModel"]) -> list["StatModel"]:
        stats_grouped = {}

        for stat in stats:
            stat_: cls = stats_grouped.setdefault(stat.campaignId, stat.copy(update={"loss": 0, "clicks": 0}))

            stat_.loss += stat.loss
            stat_.clicks += stat.clicks

        return list(stats_grouped.values())

    @classmethod
    def grouped_by_account(cls, stats: list["StatModel"]) -> list["StatModel"]:
        stats_grouped = {}

        for stat in stats:
            stat_: cls = stats_grouped.setdefault(stat.accountId, stat.copy(update={"impressions": 0}))

            stat_.impressions += stat.impressions

        return list(stats_grouped.values())


class CampaignModel(BaseModel):
    service: str
    id: int
    accountId: int
    name: str


class UserModel(BaseModel):
    firstName: str
    lastName: str
    middleName: str
    balance: Decimal


class MasterUserModel(BaseModel):
    id: int
    balance: float


class AccountModel(BaseFrozenModel):
    id: int
    name: str
    service: str
    serviceId: int
    serviceLogin: str
    servicePassword: Optional[str] = None
    status: str
    state: str
    createdAt: datetime
    balance: float
    campaigns: list[CampaignModel] = Field(default_factory=list, exclude=True)
    stats: list[StatModel] = Field(default_factory=list)

    @validator("createdAt", pre=True)
    def parse_date(cls, value: str) -> datetime:
        # Example: `2021-05-14T13:37:05+03:00`
        return datetime.fromisoformat(value)


class PayerTypeEnum(str, Enum):
    BUSINESS = "BUSINESS"
    INDIVIDUAL = "INDIVIDUAL"
    PERSON = "PERSON"


class PayerModel(BaseModel):
    name: str = ""
    id: int
    type: str


class InvoiceModel(BaseModel):
    """
    Модель безналичного счета.
    """

    id: int
