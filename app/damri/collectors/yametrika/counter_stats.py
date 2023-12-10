from datetime import date
from typing import TypeVar

from common.collectors import BaseDataCollector
from common.utils import WordToDateParser
from damri.integrations.api.yametrika.api import YaMetrikaCounterStatsAPIClient
from damri.integrations.api.yametrika.filter_params import StatsFilterParam
from damri.integrations.api.yametrika.models import (
    AdCostStatModel,
    CounterStatModel,
    DeviceCategoryStatModel,
    DeviceStatModel,
    ScreenStatModel,
    SearchStatModel,
    UrlStatModel,
)
from damri.models.base import BaseModel
from damri.utils.datetime import format_date

BaseModelType = TypeVar("BaseModelType", bound=BaseModel)


class CounterStatsDataCollector(BaseDataCollector):
    def __init__(self, counter_id: int, start: date | None = None, end: date | None = None) -> None:
        super().__init__()
        self.counter_id = counter_id
        if start:
            self.start = format_date(start)
        if end:
            self.end = format_date(end)
        elif start:
            self.end = format_date(start)

    def stats_yesterday(self) -> list[CounterStatModel]:
        """
        Конверсия и Достижения, любой цели, за вчерашний день.
        """
        start: str = WordToDateParser(previous_n_day=1, format="%Y-%m-%d")
        params = StatsFilterParam(
            ids=str(self.counter_id),
            date1=start,
            date2=start,
            metrics="ym:s:anyGoalConversionRate,ym:s:sumGoalReachesAny",  # TODO: mv to const ?
            dimensions="ym:s:lastSignDirectClickOrder",
            limit=1000,
            filters="(ym:s:isRobot=='No') and ym:s:LastSignDirectClickOrder!n",
            sort="ym:s:anyGoalConversionRate",
            group="dekaminute",
        )

        token = self._get_token()

        return YaMetrikaCounterStatsAPIClient(token=token).counter_stats(params=params)

    def _search_stats(self, start: str, end: str, sort: str) -> SearchStatModel:
        """
        Статистика по поиску: топ `sort`.
        """
        params = StatsFilterParam(
            ids=str(self.counter_id),
            date1=start,
            date2=end,
            metrics="ym:s:visits,ym:s:users,ym:s:bounceRate,ym:s:pageDepth,ym:s:avgVisitDurationSeconds",
            dimensions="ym:s:lastSearchPhrase",
            limit=1000,
            filters="(ym:s:isRobot=='No') and ym:s:LastSearchPhrase!n",
            sort=sort,
            group="day",
        )

        token = self._get_token()

        return YaMetrikaCounterStatsAPIClient(token=token).search_stats(params=params)

    def search_stats_bounce(self, start: str, end: str) -> SearchStatModel:
        """
        Статистика по поиску: топ отказы.
        """
        return self._search_stats(start, end, sort="-ym:s:bounceRate")

    def search_stats_visits(self, start: str, end: str) -> SearchStatModel:
        """
        Статистика по поиску: топ визиты.
        """
        return self._search_stats(start, end, sort="-ym:s:visits")

    def screen_stats_bounce(self, start: str, end: str) -> ScreenStatModel:
        """
        Статистика по экранам: топ отказы.
        """
        params = StatsFilterParam(
            ids=str(self.counter_id),
            date1=start,
            date2=end,
            metrics="ym:s:visits,ym:s:users,ym:s:bounceRate,ym:s:pageDepth,ym:s:avgVisitDurationSeconds",
            dimensions="ym:s:screenWidth,ym:s:screenHeight",
            limit=1000,
            filters="(ym:s:isRobot=='No') and ym:s:screenWidth!n",
            sort="-ym:s:bounceRate,-ym:s:users",
            group="day",
        )

        token = self._get_token()

        return YaMetrikaCounterStatsAPIClient(token=token).screen_stats(params=params)

    def device_stats_bounce(self, start: str, end: str) -> DeviceStatModel:
        """
        Статистика по устройствам: топ отказы.
        """
        params = StatsFilterParam(
            ids=str(self.counter_id),
            date1=start,
            date2=end,
            metrics="ym:s:visits,ym:s:users,ym:s:bounceRate,ym:s:pageDepth,ym:s:avgVisitDurationSeconds",
            dimensions="ym:s:operatingSystem",
            limit=1000,
            filters="(ym:s:isRobot=='No') and ym:s:screenWidth!n",
            sort="-ym:s:bounceRate,-ym:s:users",
            group="day",
        )

        token = self._get_token()

        return YaMetrikaCounterStatsAPIClient(token=token).device_stats(params=params)

    def device_category_stats_bounce(self, start: str, end: str) -> DeviceCategoryStatModel:
        """
        Статистика по тип устройств: топ отказы.
        """
        params = StatsFilterParam(
            ids=str(self.counter_id),
            date1=start,
            date2=end,
            metrics="ym:s:visits,ym:s:users,ym:s:bounceRate,ym:s:pageDepth,ym:s:avgVisitDurationSeconds",
            dimensions="ym:s:deviceCategory,ym:s:mobilePhone,ym:s:mobilePhoneModel",
            limit=1000,
            filters="(ym:s:isRobot=='No') and ym:s:deviceCategory!n",
            sort="-ym:s:bounceRate,-ym:s:users",
            group="day",
        )

        token = self._get_token()

        return YaMetrikaCounterStatsAPIClient(token=token).device_category_stats(params=params)

    def url_stats_bounce(self, start: str, end: str) -> UrlStatModel:
        """
        Статистика по запросам: топ отказы.
        """
        params = StatsFilterParam(
            ids=str(self.counter_id),
            date1=start,
            date2=end,
            metrics="ym:s:visits,ym:s:users,ym:s:bounceRate,ym:s:pageDepth,ym:s:avgVisitDurationSeconds",
            dimensions=(
                "ym:s:startURLPathLevel1Hash"
                ",ym:s:startURLPathLevel2Hash"
                ",ym:s:startURLPathLevel3Hash"
                ",ym:s:startURLPathLevel4Hash"
                ",ym:s:startURLHash"
            ),
            limit=1000,
            filters="(ym:s:isRobot=='No')",
            sort="-ym:s:bounceRate,-ym:s:users",
            group="day",
        )

        token = self._get_token()

        return YaMetrikaCounterStatsAPIClient(token=token).url_stats(params=params)

    def _get_base_stats(
        self, params_kwargs: dict, method: str, end: str | None = None, start: str | None = None
    ) -> BaseModelType:
        params = StatsFilterParam(
            ids=str(self.counter_id),
            date1=start or self.start,
            date2=end or self.end,
            limit=1000,
            group="day",
            **params_kwargs,
        )

        token = self._get_token()

        return getattr(YaMetrikaCounterStatsAPIClient(token=token), method)(params=params)

    def ad_cost(self) -> AdCostStatModel:
        params = dict(
            metrics=(
                "ym:ad:visits"
                ",ym:ad:users"
                ",ym:ad:clicks"
                ",ym:ad:RUBConvertedAdCost"
                ",ym:ad:bounceRate"
                ",ym:ad:sumGoalReachesAny"
            ),
            dimensions=("ym:ad:CROSS_DEVICE_LAST_SIGNIFICANTDirectPlatform"),
            sort="-ym:ad:RUBConvertedAdCost",
            direct_client_logins="tesla-zemlya-363945-nmb8",
            filters="(ym:ad:isRobot=='No') and ym:ad:CROSS_DEVICE_LAST_SIGNIFICANTDirectPlatform!n",
        )

        return self._get_base_stats(method="ad_cost", params_kwargs=params)

    def _get_token(self) -> str:
        """
        Процесс получения токена.
        """
        raise NotImplementedError
