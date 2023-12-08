from django.apps import AppConfig


class AdStatConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "ad_stat"

    def ready(self):
        from . import signals  # noqa
