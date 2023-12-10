from datetime import date, datetime

from common.models import BaseFrozenModel
from damri.integrations.base.params import BaseLimitOffsetFilterParams
from pydantic import validator


class BaseUISParamsInner(BaseLimitOffsetFilterParams):
    limit: int = 10000
    offset: int = 0
    access_token: str


class DatePeriodUISParams(BaseFrozenModel):
    date_from: str
    date_till: str

    @validator("date_from", pre=True)
    def parse_date_from(cls, value: date) -> str:
        return datetime(value.year, value.month, value.day).isoformat(sep=" ")

    @validator("date_till", pre=True)
    def parse_date_till(cls, value: date) -> str:
        return datetime(value.year, value.month, value.day).isoformat(sep=" ")


class CallReportParamsInner(DatePeriodUISParams, BaseUISParamsInner):
    pass


class CallReportParams(BaseFrozenModel):
    params: CallReportParamsInner


class MediaFileParams(BaseFrozenModel):
    params: BaseUISParamsInner
