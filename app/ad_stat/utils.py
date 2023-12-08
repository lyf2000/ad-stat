from typing import TypeVar

from ad_stat.integrations.api.click_ru.models import AccountModel
from ad_stat.models.company import Company
from ad_stat.services.collectors.click_ru import AccountData

T = TypeVar("T", bound=AccountModel | AccountData)


# TODO но у нас же есть уже проверка с yandex_account_logins
def get_selected_company_accounts(company: Company, accounts: list[T]) -> list[T]:
    if company.yandex_account_logins:
        return [account for account in accounts if account.serviceLogin in company.yandex_account_logins]

    return accounts
