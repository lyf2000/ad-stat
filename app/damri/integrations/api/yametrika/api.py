from typing import Type

from ad_stat.integrations.api.base import (
    BaseAPIClient,
    DumpDetailResponseParser,
    SourceResponseParser,
    request,
)
from damri.integrations.api.yametrika.errors import YaMetrikaTokenError
from damri.integrations.api.yametrika.filter_params import (
    ManagementCounterFilterParam,
    Param,
    StatsFilterParam,
)
from damri.integrations.api.yametrika.models import (
    AdCostStatModel,
    AdStatTotalModel,
    CounterModel,
    CounterStatModel,
    DeviceCategoryStatModel,
    DeviceStatModel,
    ScreenStatModel,
    SearchStatModel,
    UrlStatModel,
    VisitsModel,
)
from tapi_yandex_metrika import YandexMetrikaManagement, YandexMetrikaStats
from tapi_yandex_metrika.tapi_yandex_metrika import YandexMetrikaClientAdapterAbstract


class BaseYaMetrikaAPIClient(BaseAPIClient):
    def __init__(self, token: str) -> None:
        self.token = token

    API_CLASS: Type[YandexMetrikaClientAdapterAbstract] | None = None

    def _get_session(self) -> Type[YandexMetrikaClientAdapterAbstract]:
        return self.API_CLASS(access_token=self.token)


class YaMetrikaCounterStatsAPIClient(BaseYaMetrikaAPIClient):
    API_CLASS = YandexMetrikaStats

    def get(self, params: Type[Param], all_=True):
        # TODO: add pagination
        return self.session.stats().get(params=params.dict()).data

    @request(
        response_model=CounterStatModel,
        response_parser=SourceResponseParser("data"),
        detail_response_parser=DumpDetailResponseParser(
            id="dimensions.0.id",
            direct_id="dimensions.0.direct_id",
            name="dimensions.0.name",
            conversion_rate=("metrics.0", float),
            goal_reach=("metrics.1", int),
        ),
        errors=(YaMetrikaTokenError,),
    )
    def counter_stats(self, params: StatsFilterParam, all_=True) -> list[CounterStatModel]:
        # TODO: add pagination
        return self.get(params=params)

    @request(
        response_model=AdStatTotalModel,
        response_parser=SourceResponseParser("totals"),
        detail_response_parser=DumpDetailResponseParser(
            users="0",
            new_visitors_percent="1",
        ),
        errors=(YaMetrikaTokenError,),
    )
    def ad_stats_total(self, params: StatsFilterParam) -> AdStatTotalModel:
        # TODO: add pagination
        return self.get(params=params)

    @request(
        response_model=VisitsModel,
        response_parser=SourceResponseParser("data"),
        detail_response_parser=DumpDetailResponseParser(
            id="dimensions.0.id",
            goal_visits="metrics.0",
            name="dimensions.0.name",
        ),
        errors=(YaMetrikaTokenError,),
    )
    def visits_stats(self, params: StatsFilterParam) -> list[VisitsModel]:
        # TODO: add pagination
        return self.get(params=params)

    @request(
        response_model=SearchStatModel,
        detail_response_parser=DumpDetailResponseParser(
            **{
                "searches[data].text": "dimensions.0.name",
                "searches[data].visits": ("metrics.0", float),
                "searches[data].visitors": ("metrics.1", float),
                "searches[data].bounce_rate": ("metrics.2", float),
                "searches[data].page_depth": ("metrics.3", float),
                "searches[data].visit_duration": ("metrics.4", float),
                **dict(avg="totals.2"),
            }
        ),
        errors=(YaMetrikaTokenError,),
    )
    def search_stats(self, params: StatsFilterParam, all_=True) -> SearchStatModel:
        """
        Статистика по поисковым фразам.
        """
        # TODO: add pagination
        return self.get(params=params)

    @request(
        response_model=ScreenStatModel,
        detail_response_parser=DumpDetailResponseParser(
            **{
                "screens[data].width": "dimensions.0.name",
                "screens[data].height": "dimensions.1.name",
                "screens[data].visits": ("metrics.0", float),
                "screens[data].visitors": ("metrics.1", float),
                "screens[data].bounce_rate": ("metrics.2", float),
                "screens[data].page_depth": ("metrics.3", float),
                "screens[data].visit_duration": ("metrics.4", float),
                **dict(avg="totals.2"),
            }
        ),
        errors=(YaMetrikaTokenError,),
    )
    def screen_stats(self, params: StatsFilterParam, all_=True) -> ScreenStatModel:
        """
        Статистика по экранам.
        """
        # TODO: add pagination
        return self.get(params=params)

    @request(
        response_model=DeviceStatModel,
        detail_response_parser=DumpDetailResponseParser(
            **{
                "devices[data].system": "dimensions.0.name",
                "devices[data].visits": ("metrics.0", float),
                "devices[data].visitors": ("metrics.1", float),
                "devices[data].bounce_rate": ("metrics.2", float),
                "devices[data].page_depth": ("metrics.3", float),
                "devices[data].visit_duration": ("metrics.4", float),
                **dict(avg="totals.2"),
            }
        ),
        errors=(YaMetrikaTokenError,),
    )
    def device_stats(self, params: StatsFilterParam, all_=True) -> DeviceStatModel:
        """
        Статистика по устройствам.
        """
        # TODO: add pagination
        return self.get(params=params)

    @request(
        response_model=DeviceCategoryStatModel,
        detail_response_parser=DumpDetailResponseParser(
            **{
                "categories[data].category": "dimensions.0.name",
                "categories[data].phone": "dimensions.1.name",
                "categories[data].model": "dimensions.2.name",
                "categories[data].visits": ("metrics.0", float),
                "categories[data].visitors": ("metrics.1", float),
                "categories[data].bounce_rate": ("metrics.2", float),
                "categories[data].page_depth": ("metrics.3", float),
                "categories[data].visit_duration": ("metrics.4", float),
                **dict(avg="totals.2"),
            }
        ),
        errors=(YaMetrikaTokenError,),
    )
    def device_category_stats(self, params: StatsFilterParam, all_=True) -> DeviceCategoryStatModel:
        """
        Статистика по типам устройств.
        """
        # TODO: add pagination
        return self.get(params=params)

    @request(
        response_model=UrlStatModel,
        detail_response_parser=DumpDetailResponseParser(
            **{
                "urls[data].path_4": "dimensions.0.name",
                "urls[data].path_3": "dimensions.1.name",
                "urls[data].path_2": "dimensions.2.name",
                "urls[data].path_1": "dimensions.3.name",
                "urls[data].path": "dimensions.4.name",
                "urls[data].visits": ("metrics.0", float),
                "urls[data].visitors": ("metrics.1", float),
                "urls[data].bounce_rate": ("metrics.2", float),
                "urls[data].page_depth": ("metrics.3", float),
                "urls[data].visit_duration": ("metrics.4", float),
                **dict(avg="totals.2"),
            }
        ),
        errors=(YaMetrikaTokenError,),
    )
    def url_stats(self, params: StatsFilterParam, all_=True) -> UrlStatModel:
        """
        Статистика по запросам(URL).
        """
        # TODO: add pagination
        return self.get(params=params)

    @request(
        response_model=AdCostStatModel,
        detail_response_parser=DumpDetailResponseParser(
            **{
                "costs[data].": "dimensions.0.name",
                "costs[data].visits": ("metrics.0", int),
                "costs[data].visitors": ("metrics.1", int),
                "costs[data].clicks": ("metrics.2", int),
                "costs[data].ad_cost": ("metrics.3", float),
                "costs[data].bounce_rate": ("metrics.4", float),
                "costs[data].goal": ("metrics.5", int),
            }
        ),
        errors=(YaMetrikaTokenError,),
    )
    def ad_cost(self, params: StatsFilterParam) -> AdCostStatModel:
        """
        Статистика по расходам.
        """
        return self.get(params=params)

    @request()
    def dynamic(self, params: StatsFilterParam):
        return self.get(params=params)


class YaMetrikaManagementAPIClient(BaseYaMetrikaAPIClient):
    API_CLASS = YandexMetrikaManagement

    @request(response_model=CounterModel, errors=(YaMetrikaTokenError,))
    def counters(self, params: ManagementCounterFilterParam | None = None, all_=True) -> list[CounterModel]:
        """Счетчики"""

        def get(params):
            return self.session.counters().get(params=params.dict()).data

        params = params or ManagementCounterFilterParam()
        if not all_:
            return get(params)

        # TODO: move to request the pagination?
        params = ManagementCounterFilterParam()  # from start offset
        response = get(params)
        counters_data = response["counters"]

        count = response["rows"]
        while count > len(counters_data):
            params = params.next_page_filter()
            counters_data += get(params)["counters"]

        return counters_data
