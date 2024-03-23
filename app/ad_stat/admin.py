from ad_stat.models import Company
from ad_stat.tasks import send_all_bounce_reports
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

    @button(html_attrs={"style": "background-color:#ffdb4d;color:black"}, label="Отправить уведомления")
    def migrate_counters(self, request):
        self.message_user(request, SUCCESS_DATA_LOADED)
        send_all_bounce_reports(list(Company.objects.all().values_list("id", flat=True)))
        return redirect(request.META["HTTP_REFERER"])
