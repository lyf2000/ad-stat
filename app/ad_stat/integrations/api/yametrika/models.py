from decimal import Decimal

from common.models import BaseModel
from pydantic import validator


class CounterModel(BaseModel):
    """Модель Счётчика"""

    id: int
    name: str
    status: str
    site: str


class CounterStatModel(BaseModel):
    id: str  # `other` value exists
    direct_id: str
    name: str
    conversion_rate: float
    goal_reach: int


class AdStatTotalModel(BaseModel):
    users: int
    new_visitors_percent: Decimal

    @validator("new_visitors_percent", pre=True)
    def parse_new_visitors_percent(cls, value: Decimal | None = None):
        return value or Decimal("0.0")  # if `None` passed


class VisitsModel(BaseModel):
    # docs: https://metrika.yandex.ru/stat/conversion_rate

    id: int
    goal_visits: int  # Целевые визиты
    name: str | None

    @validator("name")
    def set_name(cls, name):
        return name or ""  # if `None` passed
