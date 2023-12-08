from ad_stat.choices import WeekDayChoices
from ad_stat.models import (
    Company,
    CompanyGroup,
    CompanyNotieSetting,
    CompanyResponsible,
)
from ad_stat.models.company_payment import PaymentInvoice
from ad_stat.models.notie_log import NotieLog
from ad_stat.models.payment_setting import CompanyPaymentSetting
from ad_stat.models.uis_setting import CompanyUISSetting
from ad_stat.services.cache.click_ru.user_payers import UserPayersDetailDataCache
from ad_stat.services.migrators.ya_metrika.counter import YaMetrikaCounterMigrator
from ad_stat.tasks import (
    balance_admin_notify,
    balance_companies_notify,
    daily_state_notify,
    payment_inovoices_first_step_logic_task,
    payment_inovoices_pending_payment_logic_task,
    send_all_bounce_reports,
    weekly_ads,
    weekly_aims_conversions,
)
from admin_extra_buttons.api import ExtraButtonsMixin, button
from common.admin import (
    SUCCESS_DATA_LOADED,
    SUCCESS_NOTIE_SEND_MSG,
    SUCCESS_NOTIE_SEND_MSG_MULTIPLE,
    CommaSeparatedCharField,
    IntegerChoiceField,
    MultipleIntegerChoiceField,
)
from damri.django.models.admin import ReadOnlyAdminMixin
from django import forms
from django.contrib import admin, messages
from django.shortcuts import redirect
from django.utils.html import format_html


@admin.register(CompanyGroup)
class CompanyGroupAdmin(admin.ModelAdmin):
    list_display = ("name",)

    def get_queryset(self, request):
        qs = super().get_queryset(request)

        return qs.of_user(user=request.user)


class CompanyNotieSettingInlineForm(forms.ModelForm):
    daily_days_notie = MultipleIntegerChoiceField(
        choices=WeekDayChoices.choices, widget=forms.CheckboxSelectMultiple(), required=False
    )

    class Meta:
        model = CompanyNotieSetting
        fields = (
            "daily_notie_statistics",
            "show_conversion_n_goal",
            "daily_days_notie",
            "weekly_notie_ads",
            "weekly_notie_aims_conversions",
            "weekly_notie_bounces",
            "monthly_loss_notie_statistics",
        )

    def has_changed(self, *args, **kwargs):
        if self.instance.pk is None:
            return True
        return super().has_changed(*args, **kwargs)


class CompanyNotieSettingsInline(admin.StackedInline):
    can_delete = False
    model = CompanyNotieSetting
    form = CompanyNotieSettingInlineForm


class FormSet(forms.BaseInlineFormSet):
    def get_form_kwargs(self, index):
        kwargs = super().get_form_kwargs(index)
        kwargs["parent_object"] = self.instance
        return kwargs


class CompanyPaymentSettingInlineForm(forms.ModelForm):
    payer_id = IntegerChoiceField(choices=(), required=False)

    class Meta:
        model = CompanyPaymentSetting
        exclude = tuple()

    def __init__(self, *args, **kwargs):
        company = kwargs.pop("parent_object")
        super().__init__(*args, **kwargs)
        self.fields["payer_id"].choices = (
            (payer.id, payer.name) for payer in UserPayersDetailDataCache.get(company.click_ru_user_id).payers
        )


class NotieLogInline(ReadOnlyAdminMixin, admin.TabularInline):
    model = NotieLog
    extra = 0
    fields = ("status", "type", "created", "result")
    readonly_fields = fields
    ordering = ("-created",)
    classes = ("collapse",)


class CompanyPaymentSettingInline(admin.StackedInline):
    can_delete = False
    model = CompanyPaymentSetting
    form = CompanyPaymentSettingInlineForm
    formset = FormSet


class CompanyUISSettingInline(admin.StackedInline):
    can_delete = False
    model = CompanyUISSetting


class CompanyForm(forms.ModelForm):
    telegram_ids = CommaSeparatedCharField(required=False)
    yandex_account_logins = CommaSeparatedCharField(required=False)

    class Meta:
        model = Company
        exclude = tuple()
        widgets = {"click_ru_token": forms.PasswordInput(render_value=True)}


@admin.register(Company)
class CompanyAdmin(ExtraButtonsMixin, admin.ModelAdmin):
    form = CompanyForm
    list_display = (
        "name",
        "ya_counter_id",
        "show_site_url",
        "click_ru_user_id",
        "responsible",
        "tariff",
        "telegram_ids",
    )
    search_fields = ("name", "telegram_ids", "click_ru_user_id")
    inlines = (CompanyNotieSettingsInline, CompanyPaymentSettingInline, CompanyUISSettingInline, NotieLogInline)
    actions = (
        "send_daily_state_notify",
        "send_weekly_ads",
        "send_weekly_aims_conversions",
        "send_balance_companies_notify",
        "send_all_bounce_reports",
    )
    autocomplete_fields = ("name", "telegram_ids", "click_ru_user_id")

    def get_queryset(self, request):
        qs = super().get_queryset(request)

        return qs.of_user(user=request.user)

    def show_site_url(self, company: Company):
        return format_html("<a href='http://{url}'>{url}</a>", url=company.site_url)

    @button(html_attrs={"style": "background-color:#88FF88;color:black"}, label="Отправить балансы в админку")
    def send_balance(self, request):
        self.message_user(request, SUCCESS_NOTIE_SEND_MSG)
        balance_admin_notify.delay()
        return redirect(request.META["HTTP_REFERER"])

    @button(html_attrs={"style": "background-color:#ffdb4d;color:black"}, label="Стянуть счетчики из Я.Метрика")
    def migrate_counters(self, request):
        self.message_user(request, SUCCESS_DATA_LOADED)
        YaMetrikaCounterMigrator()
        return redirect(request.META["HTTP_REFERER"])

    # Клики
    @admin.action(description="Отправить статистику по кликам за вчерашний день")
    def send_daily_state_notify(self, request, queryset):
        daily_state_notify.delay(companies=[company.id for company in queryset])
        self.message_user(request, SUCCESS_NOTIE_SEND_MSG_MULTIPLE, messages.SUCCESS)

    @admin.action(description="Отправить отчет по рекламе за предыдущую неделю")
    def send_weekly_ads(self, request, queryset):
        weekly_ads.delay(companies=[company.id for company in queryset])
        self.message_user(request, SUCCESS_NOTIE_SEND_MSG_MULTIPLE, messages.SUCCESS)

    @admin.action(description="Отправить отчет по целям и конверсиям за предыдущую неделю")
    def send_weekly_aims_conversions(self, request, queryset):
        weekly_aims_conversions.delay(companies=[company.id for company in queryset])
        self.message_user(request, SUCCESS_NOTIE_SEND_MSG_MULTIPLE, messages.SUCCESS)

    @admin.action(description="Отправить отчеты всех типов по отказам за предыдущую неделю")
    def send_all_bounce_reports(self, request, queryset):
        send_all_bounce_reports.delay(companies=[company.id for company in queryset])
        self.message_user(request, SUCCESS_NOTIE_SEND_MSG_MULTIPLE, messages.SUCCESS)

    # Баланс
    @admin.action(description="Проверить и отправить уведомлении о необходимости пополнить баланс Click.ru")
    def send_balance_companies_notify(self, request, queryset):
        balance_companies_notify.delay(companies=[company.id for company in queryset])
        self.message_user(request, SUCCESS_NOTIE_SEND_MSG_MULTIPLE, messages.SUCCESS)

    def get_inlines(self, request, obj=None):
        if obj:
            inlines = set(super().get_inlines(request, obj))
            if not obj.click_ru_user_id:
                self.message_user(request, "Укажите ID пользователя Click.ru для настройки оплат", messages.WARNING)
                inlines.remove(CompanyPaymentSettingInline)
        else:
            inlines = (CompanyNotieSettingsInline,)

        return inlines


@admin.register(CompanyResponsible)
class CompanyResponsibleAdmin(admin.ModelAdmin):
    pass


@admin.register(PaymentInvoice)
class PaymentInvoiceAdmin(admin.ModelAdmin):
    list_display = ("company", "state", "amount", "created")
    list_filter = ("company", "state")


class CompanyPaymentSettingForm(forms.ModelForm):
    payer_id = IntegerChoiceField(choices=(), required=False)

    class Meta:
        model = CompanyPaymentSetting
        exclude = tuple()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["payer_id"].choices = (
            (payer.id, payer.name)
            for payer in UserPayersDetailDataCache.get(kwargs["instance"].company.click_ru_user_id).payers
        )


@admin.register(CompanyPaymentSetting)
class CompanyPaymentSettingAdmin(ExtraButtonsMixin, admin.ModelAdmin):
    form = CompanyPaymentSettingForm
    list_display = ("company", "enabled_automatic_reports", "amount", "send_to_email")
    actions = ("send_payment_pending", "send_first_step")

    @admin.action(description="Отправить напоминание об ожидании оплаты")
    def send_payment_pending(self, request, queryset):
        payment_inovoices_pending_payment_logic_task.delay(companies=[setting.company_id for setting in queryset])
        self.message_user(request, SUCCESS_NOTIE_SEND_MSG_MULTIPLE, messages.SUCCESS)

    @admin.action(description="Создать счет на оплату и уведомить в чатах")
    def send_first_step(self, request, queryset):
        payment_inovoices_first_step_logic_task.delay(companies=[setting.company_id for setting in queryset])
        self.message_user(request, SUCCESS_NOTIE_SEND_MSG_MULTIPLE, messages.SUCCESS)


@admin.register(NotieLog)
class NotieLogAdmin(admin.ModelAdmin):
    list_display = ("company", "status", "type", "created", "result")
    # TODO: add daterange
    list_filter = ("created", "type", "status", "company")
    ordering = ("-created",)
    # TODO: add
    # def get_queryset(self, request):
    #     qs = super().get_queryset(request)

    #     return qs.of_user(user=request.user)
