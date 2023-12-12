from admin_extra_buttons.api import ExtraButtonsMixin, button
from apps.users.models import YandexProfile
from django.contrib import admin
from django.shortcuts import redirect
from django.urls import reverse_lazy


@admin.register(YandexProfile)
class YandexTokenAdmin(ExtraButtonsMixin, admin.ModelAdmin):
    list_display = ("user", "login", "first_name", "last_name", "created")
    exclude = ("data",)

    def get_queryset(self, request):
        qs = super().get_queryset(request)

        return qs.filter(user=request.user)
