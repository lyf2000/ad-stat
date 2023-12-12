from django.urls import include, path

app_name = "users"


urlpatterns = [
    path("v1/", include(("apps.users.api.v1.urls", "v1"))),
]
