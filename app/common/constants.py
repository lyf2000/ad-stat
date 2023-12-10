from decimal import Decimal
from typing import Any, TypedDict

NDS = Decimal("1.2")


class ConstanceConfig(TypedDict):
    ADMIN_TG_ID: tuple[int, str, object]  # TODO: add default class


# TODO: fix get data from db
CONSTANCE_CONFIG_ = ConstanceConfig(
    ADMIN_TG_ID=(1, "ID к админскому чату", int),
    MIN_CLICK_RU_BALANCE=(1200, "Минимальный остаток click.ru для оплаты Я.Директ", int),
    PENDING_INVOICE_DAYS=(1, "Количество дней ожидания оплаты", int),
)


class Constants(ConstanceConfig):
    pass


class Const(dict):
    def __getattribute__(self, name: str) -> Any:
        if name in self:
            return self[name]
        return super().__getattribute__(name)


_: Constants = Const(MONDAY=1, **{key: tupl[0] for key, tupl in CONSTANCE_CONFIG_.items()})  # FIXME: hint not works
