from datetime import date, datetime
from typing import Iterable, Optional, Union

from dateutil.relativedelta import relativedelta
from django.utils.timezone import now as django_now


def get_monday() -> datetime:
    return now() - relativedelta(days=now().weekday())


def now(format: str | None = None) -> datetime | str:
    now_ = django_now()

    if format:
        return now_.strftime(format)
    return now_


def format_date(_date: date, format: str = "%Y-%m-%d") -> str:
    return _date.strftime(format)


class _WordToDateParser:
    def __call__(
        self,
        last_n_previous_months: Optional[int] = None,
        last_n_previous_weeks: Optional[int] = None,
        last_n_days: Optional[int] = None,
        previous_n_day: Optional[int] = None,
        format: str | None = None,
        shift_right=False,
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
        else:
            raise AttributeError("No attr was passed")

        if shift_right:
            result = (result[0], result[1] + relativedelta(days=1))
        if not format:
            return result

        return (
            tuple(format_date(date_, format) for date_ in result)
            if isinstance(result, Iterable)
            else format_date(result, format)
        )


WordToDateParser = _WordToDateParser()
