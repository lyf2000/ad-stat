import logging
from datetime import date
from typing import Type

from ad_stat.choices import NotieLogTypes, WeekDayChoices
from ad_stat.models import Company
from ad_stat.services.collectors.uis import CompanyUISDataCollector
from ad_stat.services.collectors.ya_metrika.counter_stats import (
    CounterStatsDataCollector,
)
from ad_stat.services.noties.click_ru.base_notifier import (
    BaseStatNotifierMessageBuilderService,
)
from ad_stat.services.noties.flow.log.deliver import NotieDeliverLogFlow
from ad_stat.services.noties.stat.yadirect.ad.notifier import (
    YadirectCompanyPrevWeekAdsNotifierMessageBuilderService,
    YadirectCompanyPrevWeekAimsConversionsNotifierMessageBuilderService,
)
from common.services.base import BaseTgNotifierService
from common.utils import now, repr_number
from django.utils.timezone import timedelta

logger = logging.getLogger(__name__)


class CompaniesStatPreviousDayNotifierMessageBuilderService(BaseStatNotifierMessageBuilderService):
    def __new__(cls, *args, **kwargs):
        if now().weekday() == WeekDayChoices.MONDAY:  # for monday other collect weekend days also
            return super().__new__(CompaniesStatPreviousDayForMondayNotifierMessageBuilderService)
        return super().__new__(cls)

    def __init__(self, start_date: date, end_date: date, company: Company) -> None:
        super().__init__(start_date, end_date, company)

        # мапа списка кампаний с яндекс счетчиком конверсий
        self.click_ru_campaign_ya_metrika_map = {}
        if self.company.ya_counter_id:
            self.ya_metrika_yesterday_stats = CounterStatsDataCollector(
                counter_id=self.company.ya_counter_id
            ).stats_yesterday()
            self.click_ru_campaign_ya_metrika_map = {
                campaign.id: next(
                    (ya_stat for ya_stat in self.ya_metrika_yesterday_stats if ya_stat.name == campaign.name),
                    None,
                )
                for campaign in self.campaigns_map.values()
            }
            self.click_ru_campaign_ya_metrika_map = {
                campaign: ya_stat for campaign, ya_stat in self.click_ru_campaign_ya_metrika_map.items() if ya_stat
            }

    def get_item_msgs(self) -> list[str]:
        items = []
        for account, stats in self.account_stats.items():
            if not [stat for stat in stats if stat.loss]:
                continue

            # account_balance = ClickRuDataCacheManager.get_weekday_balance(
            #     weekday=(now() - timedelta(days=1)).weekday(), company=self.company, yandex_login=account.serviceLogin
            # )
            # account_balance = (
            #     self.get_account_balance(account) if account_balance is None else repr_number(account_balance)
            # )
            account_balance = self.get_account_balance(account)
            balance = "" if account_balance is None else f"Баланс: {account_balance}₽ "
            items.append(
                (
                    f"\n\n"
                    f"Остаток бюджета на *{account.name}*. "
                    f"{balance}"
                    f"Потратилось за вчерашний день: {self.get_account_loss(stats)} ₽"
                    + "\n\n"
                    + "\n".join(
                        [
                            (
                                f"{counter}. *{self.get_campaign_name(self.campaigns_map[stat.campaignId])}:* клики: {repr_number(stat.clicks)} = {repr_number(stat.loss)} ₽ "
                                + (
                                    f"Конверсия - {repr_number(ya_stat.goal_reach)}"
                                    if (
                                        self.company.notie_settting.show_conversion_n_goal
                                        and (
                                            ya_stat := self.click_ru_campaign_ya_metrika_map.get(
                                                self.campaigns_map[stat.campaignId].id
                                            )
                                        )
                                    )
                                    else ""
                                )
                            )
                            for counter, stat in enumerate(
                                [stat for stat in stats if stat.loss > 0 and stat.clicks > 0], start=1
                            )
                        ]
                    )
                )
            )

        return items

    def get_head_msg(self) -> str:
        base_msg = (
            "Доброе утро. Прикрепляем отчёт по расходам и баланс за "
            f'{self.start_date.strftime("%d.%m.%Y")}'
            f"\nСайт: {self.get_site_url()}"
        )

        if not self.selected_accounts:
            # balance = ClickRuDataCacheManager.get_weekday_balance(
            #     weekday=self.start_date.weekday(), company=self.company
            # )
            # balance = self.get_balance(self.user) if balance is None else repr_number(balance)
            balance = self.get_balance(self.user)
            return f"{base_msg}\nБаланс на Click.ru: {balance} ₽💰"

        return base_msg


class CompaniesStatPreviousDayForMondayNotifierMessageBuilderService(
    CompaniesStatPreviousDayNotifierMessageBuilderService
):
    def __new__(cls, *args, **kwargs):
        return object.__new__(cls)

    def get_weekend_days_items_msgs(self) -> list[str]:
        items = [
            self._get_item_msgs(date_=(now() - timedelta(days=7 - weekend_day)).date())
            for weekend_day in self.company.notie_settting.weekdays_for_monday
        ]

        items = [item for item in items if item]  # exclude `''`
        if not any(items):
            return []

        return [("Доброе утро. " if counter == 0 else "") + item for counter, item in enumerate(items)]

    def _get_item_msgs(self, date_: date) -> str:
        class_ = type(self)(start_date=date_, end_date=date_, company=self.company)

        head = "Прикрепляем отчёт по расходам за " f'{date_.strftime("%d.%m.%Y")}' f"\nСайт: {class_.get_site_url()}"

        items = []
        for account, stats in class_.account_stats.items():
            if not [stat for stat in stats if stat.loss]:
                continue

            # account_balance = ClickRuDataCacheManager.get_weekday_balance(
            #     weekday=date_.weekday(), company=self.company, yandex_login=account.serviceLogin
            # )
            # account_balance = (
            #     self.get_account_balance(account) if account_balance is None else repr_number(account_balance)
            # )
            # account_balance = self.get_account_balance(account)
            # balance = "" if account_balance is None else f"Баланс: {account_balance}₽ "
            items.append(
                f"\n\n"
                f"Остаток бюджета на *{account.name}*. "
                # f"{balance}"
                f"Потратилось: {self.get_account_loss(stats)} ₽"
                + "\n\n"
                + "\n".join(
                    [
                        (
                            f"{counter}. *{class_.get_campaign_name(class_.campaigns_map[stat.campaignId])}:* клики: {repr_number(stat.clicks)} = {repr_number(stat.loss)} ₽ "
                            + (
                                f"Конверсия - {repr_number(ya_stat.goal_reach)}"
                                if (
                                    class_.company.notie_settting.show_conversion_n_goal
                                    and (
                                        ya_stat := class_.click_ru_campaign_ya_metrika_map.get(
                                            class_.campaigns_map[stat.campaignId].id
                                        )
                                    )
                                )
                                else ""
                            )
                        )
                        for counter, stat in enumerate(
                            [stat for stat in stats if stat.loss > 0 and stat.clicks > 0], start=1
                        )
                    ]
                )
            )

        if not items:
            return ""
        items = "\n\n".join(items)
        return head + items

    def _process_composed_msgs(self, head, separated, separated_all, items) -> list[str]:
        head_current_date = (  # для последнего сообщения
            "Прикрепляем отчёт по расходам и баланс за "
            f'{self.start_date.strftime("%d.%m.%Y")}'
            f"\nСайт: {self.get_site_url()}"
        )

        if not self.selected_accounts:
            # balance = ClickRuDataCacheManager.get_weekday_balance(
            #     weekday=self.start_date.weekday(), company=self.company
            # )
            # balance = self.get_balance(self.user) if balance is None else repr_number(balance)
            balance = self.get_balance(self.user)
            head_current_date = f"{head_current_date}\nБаланс на Click.ru: {balance} ₽💰"

        sunday_report = super()._process_composed_msgs(head_current_date, False, False, items)
        if not sunday_report:
            balances = "\n".join(
                [f"*{account.name}* {self.get_account_balance(account)}₽" for account in self.account_stats.keys()]
            )
            if balances:
                sunday_report = [
                    f"Баланс{'ы' if len(self.account_stats) > 1 else ''} рекламного кабинета на понедельник:\n{balances}"
                ]

        return [*self.get_weekend_days_items_msgs(), *sunday_report]


class CompaniesLossStatPreviousMonthNotifierMessageBuilderService(BaseStatNotifierMessageBuilderService):
    def get_stat_data(self):
        return self.collector.get_stat_grouped_by_campaigns()

    def get_item_msgs(self) -> list[str]:
        msgs = []
        for account, stats in self.account_stats.items():
            msgs.append(
                "\n\n" f"*{account.name}*. Потратилось за предыдущий месяц: {self.get_account_loss(stats)} ₽" + "\n"
            )
            for counter, stat in enumerate(stats, start=1):
                msgs.append(
                    "\n"
                    f"{counter}. *{self.get_campaign_name(self.campaigns_map[stat.campaignId])}:* клики: {repr_number(stat.clicks)} = {repr_number(stat.loss)} ₽"
                )

        # Звонки
        if self.company.has_phone():
            calls = CompanyUISDataCollector(self.company).calls_report_prev_month()
            msgs.append(
                "\n\n"
                "*📞 Звонки по UIS *"
                f"\nВсего: {len(calls)}"
                f"\nПринятые: {len([call for call in calls if not call.is_lost])}"
                f"\nПропущенные: {len([call for call in calls if  call.is_lost])}"
            )

        return msgs

    def get_head_msg(self) -> str:
        if not self.selected_accounts:
            return (
                f"Доброе утро. Прикрепляем отчёт по расходам и баланс по сайту {self.get_site_url()}"
                f"\nБаланс на Click.ru: {self.get_balance(self.user)} ₽💰"
            )

        return f"Доброе утро. Прикрепляем отчёт по расходам и баланс по сайту {self.get_site_url()}"


class BaseCompanyStatNotifierService(BaseTgNotifierService):
    STAT_TYPE = ""
    MESSAGE_BUILDER_SERVICE = Type[BaseStatNotifierMessageBuilderService]

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
        with NotieDeliverLogFlow(company=self.company, type=self.STAT_TYPE) as deliver:
            msg = self.MESSAGE_BUILDER_SERVICE(
                start_date=self.start_date, end_date=self.end_date, company=self.company
            ).compose_msg()

            logger.info(f"sending to {self.company.id}")
            result = self.message_sender(chat_ids=self.company.get_telegram_ids(), msgs=msg).send_msg_chats()
            deliver(result)


class PreviousDayNotifierService(BaseCompanyStatNotifierService):
    STAT_TYPE = NotieLogTypes.DAILY_CLICK_STATS_NOTIE
    MESSAGE_BUILDER_SERVICE = CompaniesStatPreviousDayNotifierMessageBuilderService


class PreviousMonthNotifierService(BaseCompanyStatNotifierService):
    STAT_TYPE = NotieLogTypes.MONTHLY_CLICK_STATS_NOTIE
    MESSAGE_BUILDER_SERVICE = CompaniesLossStatPreviousMonthNotifierMessageBuilderService


class YadirectPrevWeekAdsNotifierService(BaseCompanyStatNotifierService):
    STAT_TYPE = NotieLogTypes.WEEKLY_YA_DIRECT_ADS_NOTIE
    MESSAGE_BUILDER_SERVICE = YadirectCompanyPrevWeekAdsNotifierMessageBuilderService


class YadirectPrevWeekAimsConversionsNotifierService(BaseCompanyStatNotifierService):
    STAT_TYPE = NotieLogTypes.WEEKLY_YA_DIRECT_AIMS_CONVERSIONS_NOTIE
    MESSAGE_BUILDER_SERVICE = YadirectCompanyPrevWeekAimsConversionsNotifierMessageBuilderService
