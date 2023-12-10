import logging
from collections import defaultdict

from ad_stat.choices import NotieLogTypes
from ad_stat.models import Company
from ad_stat.services.cache.click_ru.manager import ClickRuDataCacheManager
from ad_stat.services.collectors.click_ru import ClickRuDataCollector
from ad_stat.services.noties.click_ru.base_notifier import (
    CoreClickRuNotifierMessageBuilderService,
    ServiceEnum,
)
from ad_stat.services.noties.flow.log.deliver import NotieDeliverLogFlow
from ad_stat.utils import get_selected_company_accounts
from common.services.base import BaseTgNotifierService, TgMessage
from common.services.tg_bot import TgMessageItem
from common.utils import repr_number
from constance import config

logger = logging.getLogger(__name__)


# region admin
class BalanceAdminNotifierMessageBuilderService(CoreClickRuNotifierMessageBuilderService):
    def __init__(self, companies: list[Company]):
        self.companies = companies

    # TODO: refactor
    def get_item_msgs(self) -> list[str]:
        """
        Сбор аккаунтов по кампаниям с фильтрами по балансам аккаунтов

        1. Срочно выставить счета клиентам
                Нет денег на Яндекс и Click.ru
        2. Просьба пополнить клиентам баланс с Click.ru
                деньги в Click.ru >= MIN_CLICK_RU_BALANCE
        3. Выставить счет клиентам на пополнение Click.ru
                0 < на яндекс < min и Click.ru < MIN_CLICK_RU_BALANCE

        Returns:
            list[str]: _description_
        """
        accounts = []
        for company in self.companies:
            company_data = ClickRuDataCollector(user_id=company.click_ru_user_id).user_accounts_data()

            for account in [
                account
                for account in company_data.accounts
                if account.id in ClickRuDataCacheManager.active_account_ids(company.click_ru_user_id)
            ]:
                if (
                    account.balance <= 0.0
                    and account.service == ServiceEnum.DIRECT.name
                    and ClickRuDataCacheManager.get_company_by_id(company_data.id).balance <= 0.0
                ):  # Нет денег на Яндекс и Click.ru
                    account.company_data = company_data
                    account.company = company
                    accounts.append(account)

        result = []
        if accounts:
            result.append(
                "*I. Доброе утро. Срочно выставить счета клиентам 💰🧾:*"
                "\n"
                + "\n".join(
                    (
                        f"{counter}. {self.repr_account(account, accounts)} - {self.get_account_balance(account)} ₽"
                        f" \\ Click.ru - {repr_number(ClickRuDataCacheManager.get_company_by_id(account.company_data.id).balance)} ₽"
                        + (
                            f" \\ {self.tag_company_tg_responsible(account.company)}"
                            if account.company.responsible is not None
                            else ""
                        )
                    )
                    for counter, account in enumerate(accounts, start=1)
                )
            )

        accounts = []
        for company in self.companies:
            company_data = ClickRuDataCollector(user_id=company.click_ru_user_id).user_accounts_data()

            for account in [
                account
                for account in company_data.accounts
                if account.id in ClickRuDataCacheManager.active_account_ids(company.click_ru_user_id)
            ]:
                if (
                    account.service == ServiceEnum.DIRECT.name
                    and ClickRuDataCacheManager.get_company_by_id(company_data.id).balance
                    >= config.MIN_CLICK_RU_BALANCE
                ):  # деньги в Click.ru >= MIN_CLICK_RU_BALANCE
                    account.company_data = company_data
                    account.company = company
                    accounts.append(account)
        if accounts:
            result.append(
                "*II. Просьба пополнить клиентам баланс с Click.ru 💰🧾:*"
                "\n"
                + "\n".join(
                    (
                        f"{counter}. {self.repr_account(account, accounts)} - {self.get_account_balance(account)} ₽"
                        f" \\ Click.ru - {repr_number(ClickRuDataCacheManager.get_company_by_id(account.company_data.id).balance)} ₽"
                        + (
                            f" \\ {self.tag_company_tg_responsible(account.company)}"
                            if account.company.responsible is not None
                            else ""
                        )
                    )
                    for counter, account in enumerate(accounts, start=1)
                )
            )

        accounts = []
        for company in self.companies:
            company_data = ClickRuDataCollector(user_id=company.click_ru_user_id).user_accounts_data()

            for account in [
                account
                for account in company_data.accounts
                if account.id in ClickRuDataCacheManager.active_account_ids(company.click_ru_user_id)
            ]:
                if (
                    account.service == ServiceEnum.DIRECT.name
                    and company.min_balance_yandex is not None
                    and 0 < account.balance < company.min_balance_yandex
                    and ClickRuDataCacheManager.get_company_by_id(company_data.id).balance < config.MIN_CLICK_RU_BALANCE
                ):  # 0 < на яндекс < min и Click.ru < MIN_CLICK_RU_BALANCE
                    account.company_data = company_data
                    account.company = company
                    accounts.append(account)
        if accounts:
            result.append(
                "*III. Выставить счет клиентам на пополнение Click.ru 💰🧾:*"
                "\n"
                + "\n".join(
                    (
                        f"{counter}. {self.repr_account(account, accounts)} - {self.get_account_balance(account)} ₽"
                        f" \\ Click.ru - {repr_number(ClickRuDataCacheManager.get_company_by_id(account.company_data.id).balance)} ₽"
                        + (
                            f" \\ {self.tag_company_tg_responsible(account.company)}"
                            if account.company.responsible is not None
                            else ""
                        )
                    )
                    for counter, account in enumerate(accounts, start=1)
                )
            )

        return result

    def get_head_msg(self) -> str:
        return ""


class BalanceAdminNotifierService(BaseTgNotifierService):
    def __init__(self, companies: list[Company]) -> None:
        super().__init__()
        self.companies = companies

    def send_notie(self) -> None:
        msg = BalanceAdminNotifierMessageBuilderService(companies=self.companies).compose_msg(separated_all=True)

        logger.info(f"{type(self).__name__}: sending to {[company.id for company in self.companies]}")
        self.message_sender(msg).send_msg_admin()


class BalanceAdminNotifierMessageBuilderServiceV2(CoreClickRuNotifierMessageBuilderService):
    def __init__(self, companies: list[Company]):
        self.companies = companies

    # TODO: refactor
    def get_item_msgs(self) -> list[TgMessageItem]:
        """
        Яндекс < min и Click.ru >= MIN_CLICK_RU_BALANCE
        """
        responsibles = defaultdict(list)
        no_responsibles = []
        for company in self.companies:
            company_data = ClickRuDataCollector(user_id=company.click_ru_user_id).user_accounts_data()

            for account in [
                account
                for account in company_data.accounts
                if account.id in ClickRuDataCacheManager.active_account_ids(company.click_ru_user_id)
            ]:
                if account.service == ServiceEnum.DIRECT.name and (
                    company.min_balance_yandex is not None
                    and account.balance < company.min_balance_yandex
                    or ClickRuDataCacheManager.get_company_by_id(company_data.id).balance >= config.MIN_CLICK_RU_BALANCE
                ):
                    account.company_data = company_data
                    account.company = company

                    if company.responsible_id and company.responsible.tg_username:
                        responsibles[company.responsible].append(account)
                    else:
                        no_responsibles.append(account)

        def account_text(account) -> str:
            return (
                f"{self.get_account_balance(account)} ₽"
                + f" \\ Click.ru - {repr_number(ClickRuDataCacheManager.get_company_by_id(account.company_data.id).balance)} ₽"
            )

        msgs = [
            TgMessage(
                heading=TgMessageItem(
                    f"\n\n{self.tag_user(responsible.tg_username)} Просьба проверить балансы компаний и при необходимости выставить счета\n"
                ),
                items=[
                    TgMessageItem(f"\n{counter}. {self.repr_account(account, accounts)} - " + account_text(account))
                    for counter, account in enumerate(accounts, start=1)
                ],
            )
            for responsible, accounts in responsibles.items()
        ]

        if no_responsibles:
            msgs.append(
                TgMessage(
                    heading=TgMessageItem(f"\n\nСчета без указанных ответственных:\n"),
                    items=[TgMessageItem(account_text(account)) for account in no_responsibles],
                )
            )

        return self.compose_msgs(msgs, separate=True)

    def get_head_msg(self) -> str:
        return ""


class BalanceAdminNotifierServiceV2(BaseTgNotifierService):
    def __init__(self, companies: list[Company]) -> None:
        super().__init__()
        self.companies = companies

    def send_notie(self) -> None:
        msg = BalanceAdminNotifierMessageBuilderServiceV2(companies=self.companies).compose_msg(separated_all=True)

        logger.info(f"{type(self).__name__}: sending to {[company.id for company in self.companies]}")
        self.message_sender(msg).send_msg_admin()


# endregion


# region company chat


class BalanceCompanyNotifierMessageBuilderService(CoreClickRuNotifierMessageBuilderService):
    def __init__(self, company: Company):
        self.company = company

    # TODO: refactor
    def get_item_msgs(self) -> list[str]:
        """
        Сбор аккаунтов по компании для рассылки о балансе в чат.

        Берем только активные аккаунты
            + баланс кликру = 0
            + баланс аккаунта < минималки
        Returns:
            list[str]: _description_
        """
        result = []
        accounts = []
        company_data = ClickRuDataCollector(user_id=self.company.click_ru_user_id).user_accounts_data()
        if ClickRuDataCacheManager.get_company_by_id(company_data.id).balance != 0.0:
            return []

        selected_company_accounts = get_selected_company_accounts(self.company, company_data.accounts)
        for account in [
            account
            for account in company_data.accounts
            if account.id in ClickRuDataCacheManager.active_account_ids(self.company.click_ru_user_id)
            and account in selected_company_accounts
        ]:
            if (
                self.company.min_balance_yandex is not None
                and self.company.min_balance_yandex > account.balance
                and account.service == ServiceEnum.DIRECT.name
                and account.balance > 10
            ):
                account.company_data = company_data
                account.company = self.company
                accounts.append(account)

        if accounts:
            result.append(
                "\n\n"
                + "\n".join(
                    (
                        f"{counter}. {account.name} - {self.get_account_balance(account)} ₽"
                        f" \\ Click.ru - {repr_number(ClickRuDataCacheManager.get_company_by_id(account.company_data.id).balance)} ₽"
                    )
                    for counter, account in enumerate(accounts, start=1)
                )
            )

        return result

    def get_head_msg(self) -> str:
        return "Заканчивается баланс минимальной суммы остатка Яндекс и нет бюджета на Click.ru 💰🧾:"


class BalanceCompanyNotifierService(BaseTgNotifierService):
    STAT_TYPE = NotieLogTypes.BALANCE

    def __init__(self, company: Company) -> None:
        super().__init__()
        self.company = company

    def send_notie(self) -> None:
        with NotieDeliverLogFlow(company=self.company, type=self.STAT_TYPE) as deliver:
            msg = BalanceCompanyNotifierMessageBuilderService(company=self.company).compose_msg(separated=True)

            logger.info(f"{type(self).__name__}: sending to {self.company.id}")
            result = self.message_sender(chat_ids=self.company.get_telegram_ids(), msgs=msg).send_msg_chats()
            deliver(result)


# endregion
