from admin.base import MyAdminViews
from django.contrib import admin


class MyAdminSite(MyAdminViews, admin.AdminSite):
    index_template = "admin/index.html"
