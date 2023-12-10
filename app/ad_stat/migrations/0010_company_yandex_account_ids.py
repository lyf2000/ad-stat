# Generated by Django 4.2 on 2023-06-09 06:38

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("ad_stat", "0009_alter_company_site_url"),
    ]

    operations = [
        migrations.AddField(
            model_name="company",
            name="yandex_account_names",
            field=models.CharField(
                blank=True,
                default="",
                max_length=1024,
                verbose_name="Названия аккаунтов Яндекс.Директ на странице Click.ru (через запятую)",
            ),
        ),
    ]