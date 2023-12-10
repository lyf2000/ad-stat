from datetime import date

from apps.users.services.collectors.yandex_profile import YandexProfileDataCollector
from damri.collectors.base.collector import BaseDataCollector
from damri.integrations.api.yametrika.api import YaMetrikaCounterStatsAPIClient
from damri.integrations.api.yametrika.filter_params import StatsFilterParam
from damri.integrations.api.yametrika.models import AdStatTotalModel, VisitsModel


# TODO refactor
class Const:
    class _Dimensions:
        PERIOD_DAY = "ym:s:datePeriodday"
        GOAL = "ym:s:goalDimension"

        def __call__(self, *dimensions):
            return ",".join(dimensions)

    Dimensions = _Dimensions()

    class _Filters:
        NOT_TOBOT = "(ym:s:isRobot=='No')"
        PERIOD_DAY_N = "ym:s:datePeriodday!n"

        def __call__(self, *filters):
            return " and ".join(filters)

    Filters = _Filters()

    class _Metrics:
        USERS = "ym:s:users"  # Посетители
        PERCENT_NEW_VISITORS = "ym:s:percentNewVisitors"  # Посетители
        SUM_VISITS = "ym:s:sumVisits"

        def __call__(self, *filters):
            return ",".join(filters)

    Metrics = _Metrics()


class YametrikaAdStatsDataCollector(BaseDataCollector):
    def __init__(self, counter_id: int) -> None:
        super().__init__()
        self.counter_id = counter_id

    def get(self, start_date: date, end_date: date) -> AdStatTotalModel:
        """
        Отчеты по рекламе.

        Возвращает:
            - Посетители
            - Доля новых посетителей
        """
        params = StatsFilterParam(
            ids=str(self.counter_id),
            date1=start_date.strftime("%Y-%m-%d"),
            date2=end_date.strftime("%Y-%m-%d"),
            metrics=Const.Metrics(Const.Metrics.USERS, Const.Metrics.PERCENT_NEW_VISITORS),
            dimensions=Const.Dimensions(Const.Dimensions.PERIOD_DAY),
            limit=1000,
            filters=Const.Filters(Const.Filters.NOT_TOBOT, Const.Filters.PERIOD_DAY_N),
            group="dekaminute",
        )
        token = YandexProfileDataCollector.get_counter_yandex_profile(self.counter_id).token
        return YaMetrikaCounterStatsAPIClient(token=token).ad_stats_total(params=params)


class YametrikaVisitStatsDataCollector(BaseDataCollector):
    def __init__(self, counter_id: int) -> None:
        super().__init__()
        self.counter_id = counter_id

    def get(self, start_date: date, end_date: date) -> list[VisitsModel]:
        """
        Отчеты по целевым визитам.

        Возвращает:
            - Целевые визиты
        """
        params = StatsFilterParam(
            ids=str(self.counter_id),
            date1=start_date.strftime("%Y-%m-%d"),
            date2=end_date.strftime("%Y-%m-%d"),
            metrics=Const.Metrics(Const.Metrics.SUM_VISITS),
            dimensions=Const.Dimensions(Const.Dimensions.GOAL),
            limit=1000,
            filters=Const.Filters(Const.Filters.NOT_TOBOT),
            group="dekaminute",
        )
        token = YandexProfileDataCollector.get_counter_yandex_profile(self.counter_id).token
        return YaMetrikaCounterStatsAPIClient(token=token).visits_stats(params=params)
