from apps.users.api.v1.oauth import get_yandex_token
from django.urls import path

urlpatterns = [
    path("oauth/yandex/", get_yandex_token, name="oauth-yandex"),
]
