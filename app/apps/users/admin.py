from admin_extra_buttons.api import ExtraButtonsMixin, button
from apps.users.models import YandexProfile
from django.contrib import admin
from django.shortcuts import redirect
from django.urls import reverse_lazy


@admin.register(YandexProfile)
class YandexTokenAdmin(ExtraButtonsMixin, admin.ModelAdmin):
    list_display = ("user", "login", "first_name", "last_name", "created")

    @button(html_attrs={"style": "background-color:#ffdb4d;color:black"}, label="Добавить аккаунт Яндекс")
    def get_yandex_token(self, request):
        return redirect(reverse_lazy("users:v1:oauth-yandex"))

    def get_queryset(self, request):
        qs = super().get_queryset(request)

        return qs.filter(user=request.user)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj: YandexProfile | None = None):
        return False

    def has_delete_permission(self, request, obj: YandexProfile | None = None):
        if obj:
            return obj.user_id == request.user.id
        return True

    def has_view_permission(self, request, obj: YandexProfile | None = None):
        if obj:
            return obj.user_id == request.user.id
        return True
