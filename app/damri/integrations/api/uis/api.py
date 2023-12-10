import os
from datetime import date
from io import BytesIO
from random import randint

from damri.integrations.api.uis.models import CallReportItemModel
from damri.integrations.api.uis.params import CallReportParams, CallReportParamsInner
from damri.integrations.base.api import JRPCClient, SourceResponseParser, jrpc_request


class UISJRPCClient(JRPCClient):
    domain = "https://dataapi.uiscom.ru/v2.0"
    ACCESS_TOKEN = os.getenv("UIS_ACCESS_TOKEN")

    @property
    def base_params(self) -> dict:
        return {
            "jsonrpc": "2.0",
            "id": randint(0, 10**4),
            **super().base_params,
        }

    @property
    def base_params_inner(self):
        return {"access_token": self.ACCESS_TOKEN}

    @jrpc_request(
        response_model=CallReportItemModel,
        response_parser=SourceResponseParser("result.data"),
    )
    def calls_report(self, date_from: date, date_till: date) -> list[CallReportItemModel]:  # TODO add paginataion
        """
        Отчёт по сессиям звонков.

        Docs: https://www.comagic.ru/support/api/data-api/report/get_calls_report/"""
        method = "get.calls_report"
        params = CallReportParams(
            params=CallReportParamsInner(date_from=date_from, date_till=date_till, **self.base_params_inner)
        )

        return self.post(method, params=params)

    def get_media(self, call_session_id: int, record_id: str) -> BytesIO:
        url = f"http://app.comagic.ru/system/media/talk/{call_session_id}/{record_id}/"

        with self._download_file(url) as file:
            return file
