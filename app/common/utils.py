from datetime import date, datetime
from decimal import Decimal
from typing import Any, Callable, Iterable, Optional, TypeVar, Union

from apps.users.models import Profile
from common.constants import NDS
from dateutil.relativedelta import relativedelta
from django.utils.timezone import now as django_now


def repr_number(f: Union[Callable, Any], digits: int = 2) -> Union[Callable, str]:
    def _repr(val) -> str:
        return "{:,}".format(round(val, ndigits=digits)).replace(",", " ")

    def repr(*args, **kwargs) -> str:
        return _repr(f(*args, **kwargs))

    if callable(f):
        repr._original = f  # get the func source
        return repr

    return _repr(f)


def item_by_source(source: str, data: dict | list) -> Any:
    """Получение данных из объекта

    Args:
        source (str): путь, разделенный точками
        data (dict|list): даные

    Returns:
        Any: _description_

    Examples:
        >>> item_by_source('key1.0.key_deeper', {'key1': [{'key_deeper': 123}, 'other_key_deeper': 0], 'other_key': -1})
        123

        >>> item_by_source('0.key.1', [{'key': [0, -100, 2, 3]}, 123])
        -100
    """
    path = source.split(".")[0]

    try:
        data = data[int(path)]
    except (ValueError, TypeError):
        data = data[path]

    source_deeper = source.removeprefix(path).removeprefix(".")
    if not source_deeper:
        return data

    return item_by_source(source_deeper, data)


def get_monday() -> datetime:
    return now() - relativedelta(days=now().weekday())


class _WordToDateParser:
    def __call__(
        self,
        last_n_previous_months: Optional[int] = None,
        last_n_previous_weeks: Optional[int] = None,
        last_n_days: Optional[int] = None,
        previous_n_day: Optional[int] = None,
        last_half_month_passed=False,
        format: str | None = None,
    ) -> Union[tuple[date, date], date, str, tuple[str, str]]:
        if last_n_previous_months:
            now_ = now().replace(day=1)
            result = (
                (now_ - relativedelta(months=last_n_previous_months)).replace(day=1).date(),
                (now_ - relativedelta(days=1)).date(),
            )
        elif last_n_previous_weeks:
            monday = get_monday()
            result = (monday - relativedelta(weeks=last_n_previous_weeks)).date(), (
                monday - relativedelta(days=1)
            ).date()
        elif last_n_days:
            result = (now() - relativedelta(days=last_n_days)).date(), (now() - relativedelta(days=1)).date()
        elif previous_n_day:
            result = (now() - relativedelta(days=previous_n_day)).date()
        elif last_half_month_passed:
            if now().day > 15:
                result = (now().replace(day=1), now().replace(day=15))
            else:
                right = now().replace(day=1) - relativedelta(days=1)
                left = (now() - relativedelta(months=1)).replace(day=16)
                result = (left, right)
        else:
            raise AttributeError("No attr was passed")

        if not format:
            return result

        return (
            tuple(date_.strftime(format) for date_ in result)
            if isinstance(result, Iterable)
            else result.strftime(format)
        )


WordToDateParser = _WordToDateParser()


T = TypeVar("T", bound=float | int | Decimal)


def with_nds(value: T) -> T:
    type_ = type(value)

    return type_(Decimal(value) * NDS)


def now(format: str | None = None) -> datetime | str:
    now_ = django_now()

    if format:
        return now_.strftime(format)
    return now_


def user_admin(user=None, user_id: int | None = None) -> bool:
    return (user and user.profile.is_admin) or (
        user_id and Profile.objects.filter(user_id=user_id, is_admin=True).exists()
    )
