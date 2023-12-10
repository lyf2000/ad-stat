from ad_stat.integrations.api.errors import BaseAPIError
from tapi_yandex_metrika.exceptions import YandexMetrikaTokenError


class YaMetrikaTokenError(BaseAPIError):
    msg: str = "Ошибка доступа Я.Метрика"
    except_ = (YandexMetrikaTokenError,)
