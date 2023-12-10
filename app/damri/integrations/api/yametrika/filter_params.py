from typing import TypeVar

from common.models import BaseFrozenModel


class YaMetrikaLimitOffsetFilterParams(BaseFrozenModel):
    PAGE_SIZE_FIELD_NAME = "limit"

    offset: int = 1

    def next_page_filter(self) -> "ManagementCounterFilterParam":
        next_offset = self.offset + getattr(self, self.PAGE_SIZE_FIELD_NAME)
        return self.copy(update={"offset": next_offset})


Param = TypeVar("Param", bound=YaMetrikaLimitOffsetFilterParams)


class ManagementCounterFilterParam(YaMetrikaLimitOffsetFilterParams):
    PAGE_SIZE_FIELD_NAME = "per_page"

    per_page: int = 1000


# TODO: mv to const ?
class StatsFilterParam(YaMetrikaLimitOffsetFilterParams):
    accuracy: str | None = "full"
    limit: int = 100
    ids: str
    date1: str
    date2: str
    metrics: str
    dimensions: str
    filters: str
    sort: str | None = None
    group: str | None = None
    direct_client_logins: str = ""
    currency: str = "RUB"
    lang: str = "ru"
