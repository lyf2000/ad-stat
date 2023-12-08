# Generated by Django 4.2 on 2023-07-06 18:42

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("ad_stat", "0015_companygroup_companies"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="company",
            name="yandex_account_names",
        ),
        migrations.AddField(
            model_name="company",
            name="yandex_account_logins",
            field=models.CharField(
                blank=True,
                default="",
                max_length=1024,
                verbose_name="Логины аккаунтов Яндекс.Директ на странице Click.ru (через запятую)",
            ),
        ),
    ]
