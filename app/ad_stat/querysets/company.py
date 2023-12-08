from typing import Optional, Type

from ad_stat.choices import PaymentInvoiceState, WeekDayChoices
from ad_stat.models.company_payment import PaymentInvoice
from common.utils import user_admin
from constance import config
from django.db.models import (
    DurationField,
    ExpressionWrapper,
    F,
    OuterRef,
    QuerySet,
    Value,
)
from django.db.models.functions import Extract
from django.utils.timezone import now


class CompanyNotiesQuerySetMixin:
    # stats
    def daily_stats(self) -> QuerySet["Company"]:
        return self.click_ru().filter(notie_settting__daily_notie_statistics=True).this_day_notie()

    def monthly_loss_stats(self) -> QuerySet["Company"]:
        return self.click_ru().filter(notie_settting__monthly_loss_notie_statistics=True)

    def weekly_ads(self) -> QuerySet["Company"]:
        return self.click_ru().filter(notie_settting__weekly_notie_ads=True)

    def weekly_aims_conversions(self) -> QuerySet["Company"]:
        return self.filter(notie_settting__weekly_notie_aims_conversions=True)

    def weekly_bounces(self) -> QuerySet["Company"]:
        return self.yametrika().filter(notie_settting__weekly_notie_bounces=True)

    def this_day_notie(self, day: Optional[Type[WeekDayChoices]] = None) -> QuerySet["Company"]:
        day = now().weekday() if day is None else day  # type: ignore

        return self.filter(notie_settting__daily_days_notie__contains=[day])

    # integrations accessed
    def click_ru(self):
        return self.filter(click_ru_user_id__isnull=False)

    def yametrika(self):
        return self.filter(ya_counter_id__isnull=False)

    # filters
    def by_telegram_id(self, telegram_id: int):
        return self.filter(telegram_ids__contains=str(telegram_id))


class CompanyPaymentInvoicesQuerySetMixin:
    @property
    def payment_sq(self):
        return PaymentInvoice.objects.filter(company=OuterRef("pk")).order_by("-created")

    def _annotate_last_payment_state(self, name="payment_state", **payment_filters) -> QuerySet["Company"]:
        return self.annotate(**{name: self.payment_sq.filter(**payment_filters).values("state")[:1]})

    def _annotate_last_payment_date(self, name="payment_date", **payment_filters) -> QuerySet["Company"]:
        return self.annotate(**{name: self.payment_sq.filter(**payment_filters).values("created")[:1]})

    # region automated invoices
    def payments_automated(self) -> QuerySet["Company"]:
        """
        NOTE: Overwrite qs!!!
        Доступные для автоматической рассылки оплат:
            - enabled_automatic_reports=True
            - < min_balance_click_ru
        """
        from ad_stat.services.cache.click_ru.manager import ClickRuDataCacheManager

        # TODO refactor
        companies_allowed = [
            company.id
            for company in self.filter(payment_setting__enabled_automatic_reports=True)
            if ClickRuDataCacheManager.get_company_by_id(company.click_ru_user_id).balance
            < company.min_balance_click_ru
        ]
        return self.filter(id__in=companies_allowed)

    def payment_pending(self) -> QuerySet["Company"]:
        """
        Последняя оплата которых в `PENDING`
        """
        return self._annotate_last_payment_state().filter(payment_state__in=PaymentInvoiceState.PENDING)

    # steps
    def for_first_step_payment(self) -> QuerySet["Company"]:
        """
        Достаем только те компании, последняя оплата которых в `READY_FOR_FIRST_STEP`
        """
        return self._annotate_last_payment_state().filter(payment_state__in=PaymentInvoiceState.READY_FOR_FIRST_STEP)

    def for_pending_step(self) -> QuerySet["Company"]:
        """
        В `NOT_PAYED` % 3 == 0.
        """
        return (
            self.payment_pending()
            ._annotate_last_payment_date()
            .annotate(delta=ExpressionWrapper(Value(now()) - F("payment_date"), output_field=DurationField()))
            .annotate(
                pending_period=Extract(
                    "delta",
                    "days",
                )
                % Value(config.PENDING_INVOICE_DAYS)
            )
            .filter(pending_period=0)
        )

    # endregion


class CompanyQuerySet(CompanyNotiesQuerySetMixin, CompanyPaymentInvoicesQuerySetMixin, QuerySet):
    def of_user(self, user_id: int | None = None, user=None) -> QuerySet["Company"]:
        if user_admin(user, user_id):  # admin users have full access
            return self

        user_id = user_id or user.id

        return self.filter(company_groups__users__id__in=[user_id])
