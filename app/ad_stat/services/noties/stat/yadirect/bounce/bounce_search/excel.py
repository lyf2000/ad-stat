from datetime import time
from typing import Iterable

from ad_stat.services.noties.stat.yadirect.bounce.base import (
    BaseBounceExcelToHTMLTemplateGeneratorMixin,
)
from damri.integrations.api.yametrika.models import SearchModel
from damri.services.documents.excel.base import (
    BaseExcelGeneratorService,
    HeadingColumn,
    ItemRow,
)
from pydantic import validator


class SearchRow(ItemRow):
    text: str
    visits: int
    visitors: int
    bounce_rate: float
    page_depth: int
    visit_duration: str

    @validator("visit_duration", pre=True)
    def parse_visit_duration(cls, seconds: int) -> str:
        return time(
            hour=seconds // 3600,
            minute=seconds % 3600 // 60,
            second=seconds % 60,
        ).strftime("%M:%S")


class SearchBounceRateExcelGenerator(BaseExcelGeneratorService):
    HEADINGS = (
        HeadingColumn(name="Текст"),
        HeadingColumn(name="Визиты"),
        HeadingColumn(name="Посетители"),
        HeadingColumn(name="Отказы(%)"),
        HeadingColumn(name="Глубина просмотра"),
        HeadingColumn(name="Время на сайте"),
    )

    def __init__(self, searches: list[SearchModel]):
        super().__init__()
        self.searches = searches

    def _iterate_rows(self) -> Iterable[SearchRow]:
        for search in self.searches:
            yield SearchRow(
                text=search.text,
                visits=search.visits,
                visitors=search.visitors,
                bounce_rate=search.bounce_rate,
                page_depth=search.page_depth,
                visit_duration=search.visit_duration,
            )


class SearchBounceExcelToHTMLTemplateGenerator(
    BaseBounceExcelToHTMLTemplateGeneratorMixin, SearchBounceRateExcelGenerator
):
    REPORT_NAME = "Отчет по отказам по поисковым фразам (SEO)"
