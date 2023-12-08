import logging
from datetime import date, datetime
from typing import Optional, Union

from ad_stat.models.company import Company
from ad_stat.models.company_settings import CompanyNotieSetting
from ad_stat.services.cache.click_ru.periodic import (
    WeekDayClickRuBalanceCacheTaskCollector,
)
from ad_stat.services.noties.click_ru.balance.notifier import (
    BalanceAdminNotifierService,
    BalanceAdminNotifierServiceV2,
    BalanceCompanyNotifierService,
)
from ad_stat.services.noties.click_ru.stat.notifier import (
    PreviousDayNotifierService,
    PreviousMonthNotifierService,
    YadirectPrevWeekAdsNotifierService,
    YadirectPrevWeekAimsConversionsNotifierService,
)
from ad_stat.services.noties.stat.yadirect.ad.cost.notifier import (
    YadirectCompanyAdCostStatNotifierStatService,
)
from ad_stat.services.noties.stat.yadirect.bounce.bounce_device.notifier import (
    YadirectCompanyBounceDeviceStatService,
)
from ad_stat.services.noties.stat.yadirect.bounce.bounce_device_category.notifier import (
    YadirectCompanyBounceDeviceCategoryStatService,
)
from ad_stat.services.noties.stat.yadirect.bounce.bounce_screen.notifier import (
    YadirectCompanyBounceScreenStatService,
)
from ad_stat.services.noties.stat.yadirect.bounce.bounce_search.notifier import (
    YadirectCompanyBounceSearchNotifierService,
)
from ad_stat.services.noties.stat.yadirect.bounce.bounce_url.notifier import (
    YadirectCompanyBounceUrlStatNotifierStatService,
)
from ad_stat.services.noties.stat.yadirect.top.search.notifier import (
    YadirectCompanyTopSearchStatService,
)
from celery import shared_task
from common.utils import WordToDateParser, now
from flows.payment.invoice.automatic_generate.flow import FirstStepPaymentInvoiceFlow
from flows.payment.invoice.payment_pending.flow import PendingPaymentInvoiceFlow

SERVICE_MAP = dict(
    daily=PreviousDayNotifierService,
    monthly_loss=PreviousMonthNotifierService,
    weekly_ads=YadirectPrevWeekAdsNotifierService,
    weekly_aims_conversions=YadirectPrevWeekAimsConversionsNotifierService,
    search_bounce=YadirectCompanyBounceSearchNotifierService,
    search_visits=YadirectCompanyTopSearchStatService,
    search_ad_cost=YadirectCompanyAdCostStatNotifierStatService,
    screen_bounce=YadirectCompanyBounceScreenStatService,
    device_bounce=YadirectCompanyBounceDeviceStatService,
    device_category_bounce=YadirectCompanyBounceDeviceCategoryStatService,
    url_bounce=YadirectCompanyBounceUrlStatNotifierStatService,
)


logger = logging.getLogger("ad_stat.tasks")


# region clicks stat


@shared_task
def daily_state_notify(date_parser_kwargs: dict | None = None, companies: Optional[list[int]] = None):
    companies = list(
        (Company.objects.filter(id__in=companies) if companies else Company.objects.daily_stats()).select_related(
            "notie_settting"
        )
    )
    date_parser_kwargs = date_parser_kwargs or {"last_n_days": 1}

    for company in companies:
        start_date, end_date = WordToDateParser(**date_parser_kwargs, format="%Y-%m-%d")
        state_notify.delay(
            start_date=start_date,
            end_date=end_date,
            builder_name="daily",
            company_id=company.id,
        )


@shared_task
def weekly_ads(date_parser_kwargs: dict | None = None, companies: Optional[list[int]] = None):
    companies = list(Company.objects.filter(id__in=companies) if companies else Company.objects.weekly_ads())
    date_parser_kwargs = date_parser_kwargs or {"last_n_previous_weeks": 1}

    for company in companies:
        start_date, end_date = WordToDateParser(**date_parser_kwargs, format="%Y-%m-%d")
        state_notify.delay(
            start_date=start_date,
            end_date=end_date,
            builder_name="weekly_ads",
            company_id=company.id,
        )


@shared_task
def weekly_aims_conversions(date_parser_kwargs: dict | None = None, companies: Optional[list[int]] = None):
    companies = list(
        Company.objects.filter(id__in=companies) if companies else Company.objects.weekly_aims_conversions()
    )
    date_parser_kwargs = date_parser_kwargs or {"last_n_previous_weeks": 1}

    for company in companies:
        start_date, end_date = WordToDateParser(**date_parser_kwargs, format="%Y-%m-%d")
        state_notify.delay(
            start_date=start_date,
            end_date=end_date,
            builder_name="weekly_aims_conversions",
            company_id=company.id,
        )


@shared_task
def monthly_loss_state_notify(date_parser_kwargs: dict | None = None, companies: Optional[list[int]] = None):
    companies = list(Company.objects.filter(id__in=companies) if companies else Company.objects.monthly_loss_stats())
    date_parser_kwargs = date_parser_kwargs or {"last_n_previous_months": 1}

    for company in companies:
        start_date, end_date = WordToDateParser(**date_parser_kwargs, format="%Y-%m-%d")
        state_notify.delay(
            start_date=start_date,
            end_date=end_date,
            company_id=company.id,
            builder_name="monthly_loss",
        )


# endregion

# region search


@shared_task
def send_all_bounce_reports(companies: list[int] | None = None):
    weekly_search_bounce_notify.delay(companies=companies)
    weekly_screen_bounce_notify.delay(companies=companies)
    weekly_device_category_bounce_notify.delay(companies=companies)
    weekly_device_bounce_notify.delay(companies=companies)
    weekly_url_bounce_notify.delay(companies=companies)


@shared_task
def weekly_search_bounce_notify(date_parser_kwargs: dict | None = None, companies: Optional[list[int]] = None):
    """
    Топ страниц с большим коэффициентом отказов
    по поиску за предыдущие недели.
    """
    companies = list(Company.objects.filter(id__in=companies) if companies else Company.objects.weekly_bounces())
    date_parser_kwargs = date_parser_kwargs or {"last_n_previous_weeks": 1}

    for company in companies:
        start_date, end_date = WordToDateParser(**date_parser_kwargs, format="%Y-%m-%d")
        state_notify.delay(
            start_date=start_date,
            end_date=end_date,
            builder_name="search_bounce",
            company_id=company.id,
        )


@shared_task
def weekly_search_visits_notify(date_parser_kwargs: dict | None = None, companies: Optional[list[int]] = None):
    """
    Топ страниц с большим коэффициентом визитов
    по поиску за предыдущие недели.
    """
    companies = list(Company.objects.filter(id__in=companies) if companies else Company.objects.weekly_bounces())
    date_parser_kwargs = date_parser_kwargs or {"last_n_previous_weeks": 1}

    for company in companies:
        start_date, end_date = WordToDateParser(**date_parser_kwargs, format="%Y-%m-%d")
        state_notify.delay(
            start_date=start_date,
            end_date=end_date,
            builder_name="search_visits",
            company_id=company.id,
        )


@shared_task
def search_ad_cost_notify(date_parser_kwargs: dict | None = None, companies: Optional[list[int]] = None):
    """
    Отчет по поисковым запросам с контекстной рекламы
    """
    companies = list(Company.objects.filter(id__in=companies) if companies else Company.objects.weekly_bounces())
    date_parser_kwargs = date_parser_kwargs or {"last_n_previous_weeks": 1}

    for company in companies:
        start_date, end_date = WordToDateParser(**date_parser_kwargs, format="%Y-%m-%d")
        state_notify.delay(
            start_date=start_date,
            end_date=end_date,
            builder_name="search_ad_cost",
            company_id=company.id,
        )


# endregion

# region screen


@shared_task
def weekly_screen_bounce_notify(date_parser_kwargs: dict | None = None, companies: Optional[list[int]] = None):
    """
    Топ страниц с большим коэффициентом отказов
    по экранам за предыдущие недели.
    """
    companies = list(Company.objects.filter(id__in=companies) if companies else Company.objects.weekly_bounces())
    date_parser_kwargs = date_parser_kwargs or {"last_n_previous_weeks": 1}

    for company in companies:
        start_date, end_date = WordToDateParser(**date_parser_kwargs, format="%Y-%m-%d")
        state_notify.delay(
            start_date=start_date,
            end_date=end_date,
            builder_name="screen_bounce",
            company_id=company.id,
        )


# endregion
# region device


@shared_task
def weekly_device_bounce_notify(date_parser_kwargs: dict | None = None, companies: Optional[list[int]] = None):
    """
    Топ страниц с большим коэффициентом отказов
    по устройствам за предыдущие недели.
    """
    companies = list(Company.objects.filter(id__in=companies) if companies else Company.objects.weekly_bounces())
    date_parser_kwargs = date_parser_kwargs or {"last_n_previous_weeks": 1}

    for company in companies:
        start_date, end_date = WordToDateParser(**date_parser_kwargs, format="%Y-%m-%d")
        state_notify.delay(
            start_date=start_date,
            end_date=end_date,
            builder_name="device_bounce",
            company_id=company.id,
        )


# endregion

# region device category


@shared_task
def weekly_device_category_bounce_notify(date_parser_kwargs: dict | None = None, companies: Optional[list[int]] = None):
    """
    Топ страниц с большим коэффициентом отказов
    по типам устройств за предыдущие недели.
    """
    companies = list(Company.objects.filter(id__in=companies) if companies else Company.objects.weekly_bounces())
    date_parser_kwargs = date_parser_kwargs or {"last_n_previous_weeks": 1}

    for company in companies:
        start_date, end_date = WordToDateParser(**date_parser_kwargs, format="%Y-%m-%d")
        state_notify.delay(
            start_date=start_date,
            end_date=end_date,
            builder_name="device_category_bounce",
            company_id=company.id,
        )


# endregion

# region url


@shared_task
def weekly_url_bounce_notify(date_parser_kwargs: dict | None = None, companies: Optional[list[int]] = None):
    """
    Топ страниц с большим коэффициентом отказов
    по типам запросам за предыдущие недели.
    """
    companies = list(Company.objects.filter(id__in=companies) if companies else Company.objects.weekly_bounces())
    date_parser_kwargs = date_parser_kwargs or {"last_n_previous_weeks": 1}

    for company in companies:
        start_date, end_date = WordToDateParser(**date_parser_kwargs, format="%Y-%m-%d")
        state_notify.delay(
            start_date=start_date,
            end_date=end_date,
            builder_name="url_bounce",
            company_id=company.id,
        )


# endregion


@shared_task
def state_notify(
    start_date: Union[date, str],
    end_date: Union[date, str],
    builder_name: str,
    company_id: int,
):
    if isinstance(start_date, str):
        start_date = datetime.strptime(start_date, "%Y-%m-%d")
    if isinstance(end_date, str):
        end_date = datetime.strptime(end_date, "%Y-%m-%d")

    company = Company.objects.filter(id=company_id).get()
    SERVICE_MAP[builder_name](
        start_date=start_date,
        end_date=end_date,
        company=company,
    ).send_notie()


# from ad_stat.tasks import state_notify
# from ad_stat.models import Company
# start = "2023-09-05"
# end = "2023-09-21"
# for c in Company.objects.weekly_bounces():
#     for i in (
#         "search_bounce",
#         "screen_bounce",
#         "device_bounce",
#         "device_category_bounce",
#         "url_bounce",
#     ):
#         state_notify.delay(start, end, i, c)


@shared_task
def balance_admin_notify(companies: Optional[list[int]] = None):
    companies = list(Company.objects.filter(id__in=companies) if companies else Company.objects.click_ru())

    BalanceAdminNotifierService(companies=companies).send_notie()


@shared_task
def balance_admin_notify_v2(companies: Optional[list[int]] = None):
    companies = list(Company.objects.filter(id__in=companies) if companies else Company.objects.click_ru())

    BalanceAdminNotifierServiceV2(companies=companies).send_notie()


@shared_task
def balance_companies_notify(companies: list[int] | None = None):
    companies = list(Company.objects.filter(id__in=companies) if companies else Company.objects.click_ru())

    for company in companies:
        balance_company_notify.delay(company_id=company.id)


@shared_task
def balance_company_notify(company_id: int):
    company = Company.objects.get(id=company_id)

    BalanceCompanyNotifierService(company=company).send_notie()


# region payment invoices


@shared_task
def call_payment_invoice_flows():
    """
    Вызов проверки по состоянию счетов на Click.ru и выставление
    счетов на оплату.
    Также напоминание о неуплаченных счетах.
    """
    payment_inovoices_first_step_logic_task.delay()
    payment_inovoices_pending_payment_logic_task.delay()


# region first step


@shared_task
def payment_inovoices_first_step_logic_task(companies: list[int] | None = None):
    """
    Cоздание первых счетов для оплаты c уведомлением
    компаниям с < `min_balance_click_ru`.

    Docs:
        https://docs.google.com/document/d/10LQ1sjd09aXBg8HoeukOacr-qkw0qWMhLRJmgXwforw/edit
    """
    companies = list(
        (
            Company.objects.filter(id__in=companies)
            if companies
            else Company.objects.payments_automated().for_first_step_payment()
        )
    )

    for company in companies:
        payment_inovoice_first_step_for_company_logic_task.delay(company_id=company.id)


@shared_task
def payment_inovoice_first_step_for_company_logic_task(company_id: int):
    """
    Cоздание первого счета для оплаты c уведомлением.

    Docs:
        https://docs.google.com/document/d/10LQ1sjd09aXBg8HoeukOacr-qkw0qWMhLRJmgXwforw/edit
    """
    FirstStepPaymentInvoiceFlow(company_id=company_id)()


# endregion first step
# region pending payment


@shared_task
def payment_inovoices_pending_payment_logic_task(companies: list[int] | None = None):
    """
    Логика напоминания о необходимости в оплате.

    Docs:
        https://docs.google.com/document/d/10LQ1sjd09aXBg8HoeukOacr-qkw0qWMhLRJmgXwforw/edit
    """
    companies = list(
        (
            Company.objects.filter(id__in=companies)
            if companies
            else Company.objects.payments_automated().for_pending_step()
        )
    )

    for company in companies:
        payment_inovoices_pending_payment_for_company_logic_task.delay(company_id=company.id)


@shared_task
def payment_inovoices_pending_payment_for_company_logic_task(company_id: int):
    """
    Напоминание компании о необходимости в оплате.

    Docs:
        https://docs.google.com/document/d/10LQ1sjd09aXBg8HoeukOacr-qkw0qWMhLRJmgXwforw/edit
    """
    PendingPaymentInvoiceFlow(company_id=company_id)()


# endregion pending payment
# endregion payment invoices


# region utils


def top_up_settings(company_ids: list[int] | None = None):
    """
    Добавить недостающие настройки компаниям.
    """
    settings = []
    for company in (
        Company.objects.filter(id__in=company_ids)
        if company_ids
        else Company.objects.filter(notie_settting__isnull=True)
    ):
        settings.append(CompanyNotieSetting(company=company))

    logger.info(f"Trying to create setting for companies {[setting.company.id for setting in settings]}")
    res = CompanyNotieSetting.objects.bulk_create(settings, batch_size=500)
    logger.info(f"Created: {res}")


# endregion


# region cache


@shared_task
def cache_weekday_click_ru_balance_for_today():
    WeekDayClickRuBalanceCacheTaskCollector(weekday=now().weekday())()


# endregion
