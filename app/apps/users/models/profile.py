from common.models import TimeStampModel
from django.conf import settings
from django.db import models


class Profile(TimeStampModel):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="Основной польователь",
        related_name="profile",
    )
    is_admin = models.BooleanField(default=False, verbose_name="Админ")

    class Meta:
        verbose_name = "Профиль"
        verbose_name_plural = "Профили"

    def __str__(self):
        return f"Профиль {self.user}"
