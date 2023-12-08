import logging
from datetime import date, datetime
from typing import Optional, Union

from ad_stat.models.company import Company
from ad_stat.services.noties.stat.yadirect.bounce.bounce_search.notifier import (
    YadirectCompanyBounceSearchNotifierService,
)
from celery import shared_task
from common.utils import WordToDateParser

SERVICE_MAP = dict(
    search_bounce=YadirectCompanyBounceSearchNotifierService,
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


@shared_task
def send_all_bounce_reports(companies: list[int] | None = None):
    weekly_search_bounce_notify.delay(companies=companies)


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
