import logging
from datetime import date

from ad_stat.choices import NotieLogTypes
from ad_stat.models import Company
from ad_stat.services.collectors.ya_metrika.counter_stats import (
    CounterStatsDataCollector,
)
from ad_stat.services.noties.click_ru.base_notifier import (
    BaseStatNotifierMessageBuilderService,
)
from ad_stat.services.noties.stat.yadirect.bounce.bounce_search.excel import (
    SearchBounceExcelToHTMLTemplateGenerator,
)
from common.services.base import BaseNotifierMessageBuilderService, BaseNotifierService
from common.services.tg_bot import TgBotMessageSenderService, TgMessageItem
from damri.services.documents.base import html_to_pdf

logger = logging.getLogger(__name__)


class BaseTgNotifierService(BaseNotifierService):
    def __init__(self) -> None:
        self.message_sender = TgBotMessageSenderService


class BaseCompanyStatNotifierService(BaseTgNotifierService):
    STAT_TYPE = ""
    MESSAGE_BUILDER_SERVICE = BaseStatNotifierMessageBuilderService

    def __init__(
        self,
        company: Company,
        start_date: date,
        end_date: date,
    ) -> None:
        super().__init__()
        self.start_date: date = start_date
        self.end_date: date = end_date
        self.company = company

    def _send_notie(self) -> None:
        msg = self.MESSAGE_BUILDER_SERVICE(
            start_date=self.start_date, end_date=self.end_date, company=self.company
        ).compose_msg()

        logger.info(f"sending to {self.company.id}")
        result = self.message_sender(chat_ids=self.company.get_telegram_ids(), msgs=msg).send_msg_chats()


class YadirectCompanyBounceSearchStatNotifierMessageBuilderService(BaseNotifierMessageBuilderService):
    """
    Топ страниц с большим коэффициентом отказов по поиску.

    Docs: https://devmarkcrm.ru/#/user-tasks/11744
    """

    def __init__(self, start_date: date, end_date: date, company: Company) -> None:
        super().__init__()
        self.start_date = start_date
        self.end_date = end_date
        self.company = company

        start, end = self.start_date.strftime("%Y-%m-%d"), self.end_date.strftime("%Y-%m-%d")
        self.search_stats = CounterStatsDataCollector(company.ya_counter_id).search_stats_bounce(start, end)
        self.searches_selected = self.search_stats.searches

    def get_head_msg(self) -> TgMessageItem | None:
        if not self.searches_selected:
            return None

        msg = (
            f"Вечер добрый. *Сформирован отчет* по отказам по поисковым запросам (SEO) сайта: *{self.company.site_url}*"
            f"\nДаты: {self.start_date.strftime('%d.%m')} – {self.end_date.strftime('%d.%m')}"
            f"\n\nСредний показатель отказов {self.search_stats.avg:.2f}%. Файл-отчет со страницами"
        )

        return TgMessageItem(
            msg=msg,
            attachments=[
                (
                    self.get_document(),
                    f"{SearchBounceExcelToHTMLTemplateGenerator.REPORT_NAME.replace(' ', '_')}.pdf",
                )
            ],
        )

    def get_document(self) -> bytes:
        return html_to_pdf(
            SearchBounceExcelToHTMLTemplateGenerator(
                searches=self.searches_selected,
                site_url=self.company.site_url,
                date_from=self.start_date,
                date_to=self.end_date,
                bounce_rate=f"{self.search_stats.avg:.2f}",
            ).generate()
        )


class YadirectCompanyBounceSearchNotifierService(BaseCompanyStatNotifierService):
    """
    Сервис для отправки сообщения с большим коэффициентом отказов по поиску.
    """

    STAT_TYPE = NotieLogTypes.SEARCH_URL_BOUNCE_TOP
    MESSAGE_BUILDER_SERVICE = YadirectCompanyBounceSearchStatNotifierMessageBuilderService
