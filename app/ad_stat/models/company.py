from typing import List

from ad_stat.choices import CompanyTariffChoices
from ad_stat.querysets.company import CompanyQuerySet
from common.models import BaseDjangoModel, null
from django.db import models


class Company(BaseDjangoModel):
    name = models.CharField(max_length=255, verbose_name="Название")
    site_url = models.CharField(max_length=200, verbose_name="Ссылка на сайт", default="", blank=True)
    client_contact = models.CharField(max_length=25, verbose_name="Контакт клиента", default="", blank=True)
    number = models.CharField(max_length=25, verbose_name="Контактный номер", default="", blank=True)

    # integrations data
    ya_counter_id = models.IntegerField(verbose_name="ID счетчика metrika.yandex.ru", **null)
    telegram_ids = models.CharField(
        max_length=255,
        verbose_name="Telegram id (через запятую)",
        default="",
        blank=True,
    )

    objects = CompanyQuerySet.as_manager()

    class Meta:
        verbose_name = "Компания"
        verbose_name_plural = "Компании"

    def __str__(self) -> str:
        return f"{self.name}"

    def get_telegram_ids(self) -> List[int]:
        return [int(id) for id in self.telegram_ids.split(",")]
