import os
from datetime import date, time

from damri.services.documents.excel.base import (
    ExcelToHTMLTemplateGeneratorMixin,
    ItemRow,
)
from pydantic import validator


class BaseRow(ItemRow):
    visits: int
    visitors: int
    bounce_rate: float
    page_depth: int
    visit_duration: str

    @validator("bounce_rate", pre=True)
    def parse_bounce_rate(cls, bounce_rate: float) -> str:
        return f"{bounce_rate:.2f}"

    @validator("visit_duration", pre=True)
    def parse_visit_duration(cls, seconds: int) -> str:
        return time(
            hour=seconds // 3600,
            minute=seconds % 3600 // 60,
            second=seconds % 60,
        ).strftime("%M:%S")

    def values(self):  # fix order, firstly of child
        parent_keys = self.keys()[:5]
        return [getattr(self, key) for key in self.keys() if key not in parent_keys] + [
            getattr(self, key) for key in self.keys() if key in parent_keys
        ]


class BaseYadirectStatsExcelToHTMLTemplateGeneratorMixin(ExcelToHTMLTemplateGeneratorMixin):
    TEMPLATE_PATH = ""

    def __init__(self, site_url: str, date_from: date, date_to: date, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.site_url = site_url
        self.date_from, self.date_to = date_from, date_to

    def get_context(self) -> dict:
        return {
            "site_url": self.site_url,
            "report_name": self.REPORT_NAME,
            "date_range": f"{self.date_from.strftime('%d.%m')} - {self.date_to.strftime('%d.%m')}",
            **super().get_context(),
        }


class BaseBounceExcelToHTMLTemplateGeneratorMixin(BaseYadirectStatsExcelToHTMLTemplateGeneratorMixin):
    TEMPLATE_PATH = os.path.join("ad_stat", "bounce-stats", "base.html")

    def __init__(self, bounce_rate: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bounce_rate = bounce_rate

    def get_context(self) -> dict:
        return {
            "bounce_rate": self.bounce_rate,
            **super().get_context(),
        }
