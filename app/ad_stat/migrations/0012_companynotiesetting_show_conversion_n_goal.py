# Generated by Django 4.2 on 2023-06-28 18:45

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("ad_stat", "0011_merge_20230611_1812"),
    ]

    operations = [
        migrations.AddField(
            model_name="companynotiesetting",
            name="show_conversion_n_goal",
            field=models.BooleanField(
                default=False, verbose_name="Показывать данные коверсии и цели в отчете"
            ),
        ),
    ]