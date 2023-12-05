from common.models import TimeStampModel
from django.conf import settings
from django.db import models


def default_dict():
    return {}


class YandexProfile(TimeStampModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Основной польователь"
    )

    login = models.CharField(max_length=128, verbose_name="Логин")
    email = models.EmailField(verbose_name="Почта")
    first_name = models.CharField(max_length=128, verbose_name="Имя")
    last_name = models.CharField(max_length=128, verbose_name="Фамилия")

    token = models.CharField(max_length=532, verbose_name="Токен доступа")  # TODO encode
    data = models.JSONField(verbose_name="Data", default=default_dict)

    class Meta:
        verbose_name = "Пользователь Яндекс"
        verbose_name_plural = "Пользователи Яндекс"

    def __str__(self) -> str:
        return f"Пользователь Яндекс {self.login}"

    def decoded_token(self) -> str:
        return self.token

    @classmethod
    def token_encode(cls, token: str) -> str:
        return token
