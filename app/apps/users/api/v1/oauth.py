import os

from apps.users.flows.models.oauth.yandex import YandexTokenCreatorFlow
from apps.users.models import YandexProfile
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response


@api_view(["GET"])
@permission_classes((AllowAny,))
def get_yandex_token(request):
    if code := request.query_params.get("code"):
        token = YandexTokenCreatorFlow()(code=code, user=request.user)
        return Response(data={"token": token})

    return HttpResponseRedirect(os.getenv("YAMETRIKA_OAUTH_GET_CODE"))
