from datetime import date
from decimal import Decimal

from damri.models.base import BaseModel
from pydantic import Field, validator


class CounterModel(BaseModel):
    """Модель Счётчика"""

    id: int
    name: str
    status: str
    site: str


class CounterStatModel(BaseModel):
    id: str  # `other` value exists
    direct_id: str
    name: str
    conversion_rate: float
    goal_reach: int


class AdStatTotalModel(BaseModel):
    users: int
    new_visitors_percent: Decimal

    @validator("new_visitors_percent", pre=True)
    def parse_new_visitors_percent(cls, value: Decimal | None = None):
        return value or Decimal("0.0")  # if `None` passed


class VisitsModel(BaseModel):
    # docs: https://metrika.yandex.ru/stat/conversion_rate

    id: int
    goal_visits: int  # Целевые визиты
    name: str | None

    @validator("name", pre=True)
    def set_name(cls, name):
        return name or ""  # if `None` passed


class UserModel(BaseModel):
    """Модель Пользователя"""

    id: int
    login: str
    client_id: str  # 'd933ecf8230942f1851ae2dd074ef6cd'
    display_name: str  # 'rdwork'
    real_name: str
    first_name: str
    last_name: str
    sex: str | None = None  # 'male'
    default_email: str
    birthday: date | None = None  # '1990-01-11'


class BounceStatModel(BaseModel):
    """Данные отказа"""

    visits: int  # Визиты
    visitors: int  # Посетители
    page_depth: int  # Глубина просмотра
    visit_duration: int  # Длительность в секундах
    bounce_rate: float  # Отказы в %


class SearchModel(BounceStatModel):
    """Модель Поиска"""

    text: str


class SearchStatModel(BaseModel):
    """Модель Статистики Поиска"""

    avg: float
    searches: list[SearchModel] = Field(default_factory=list)


class ScreenModel(BounceStatModel):
    """Модель Экрана"""

    width: int  # Ширина
    height: int  # Высота


class ScreenStatModel(BaseModel):
    """Модель Статистики Экрана"""

    avg: float
    screens: list[ScreenModel] = Field(default_factory=list)


class DeviceModel(BounceStatModel):
    """Модель Устройства"""

    system: str  # ОС


class DeviceStatModel(BaseModel):
    """Модель Статистики Устройства"""

    avg: float
    devices: list[DeviceModel] = Field(default_factory=list)


class DeviceCategoryModel(BounceStatModel):
    """Модель Типа Устройства"""

    category: str
    phone: str | None
    model: str | None


class DeviceCategoryStatModel(BaseModel):
    """Модель Статистики Типов Устройств"""

    avg: float
    categories: list[DeviceCategoryModel] = Field(default_factory=list)


class UrlModel(BounceStatModel):
    """Модель Запроса"""

    path_1: str | None
    path_2: str | None
    path_3: str | None
    path_4: str | None
    path: str


class UrlStatModel(BaseModel):
    """Модель Статистики Типов Устройств"""

    avg: float
    urls: list[UrlModel] = Field(default_factory=list)


class AdCostModel(BaseModel):
    """Данные отказа"""

    visits: int  # Визиты
    visitors: int  # Посетители
    clicks: int  # Посетители
    bounce_rate: float  # Отказы в %
    ad_cost: float  # Расходы
    goal: int  # Достижения любой цели


class AdCostStatModel(BaseModel):
    """Модель Статистики Расходов"""

    costs: list[AdCostModel] = Field(default_factory=list)
