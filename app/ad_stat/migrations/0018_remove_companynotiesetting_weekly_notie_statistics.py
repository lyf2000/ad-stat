# Generated by Django 4.2 on 2023-07-11 15:10

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        (
            "ad_stat",
            "0017_rename_daily_notie_companynotiesetting_daily_notie_statistics_and_more",
        ),
    ]

    operations = [
        migrations.RemoveField(
            model_name="companynotiesetting",
            name="weekly_notie_statistics",
        ),
    ]
