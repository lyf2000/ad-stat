from ad_stat.models import Company
from ad_stat.services.migrators.ya_metrika.counter import YaMetrikaCounterMigrator
from admin_extra_buttons.api import ExtraButtonsMixin, button
from common.admin import SUCCESS_DATA_LOADED
from django.contrib import admin
from django.shortcuts import redirect
from django.utils.html import format_html


@admin.register(Company)
class CompanyAdmin(ExtraButtonsMixin, admin.ModelAdmin):
    list_display = (
        "name",
        "ya_counter_id",
        "show_site_url",
        "telegram_ids",
    )
    search_fields = ("name", "telegram_ids")
    autocomplete_fields = ("name", "telegram_ids")

    def show_site_url(self, company: Company):
        return format_html("<a href='http://{url}'>{url}</a>", url=company.site_url)

    @button(html_attrs={"style": "background-color:#ffdb4d;color:black"}, label="Стянуть счетчики из Я.Метрика")
    def migrate_counters(self, request):
        self.message_user(request, SUCCESS_DATA_LOADED)
        YaMetrikaCounterMigrator()
        return redirect(request.META["HTTP_REFERER"])
