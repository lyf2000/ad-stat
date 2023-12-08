# Generated by Django 4.2 on 2023-05-14 12:18

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("ad_stat", "0004_companynotiesetting_monthly_loss_notie"),
    ]

    operations = [
        migrations.AddField(
            model_name="companynotiesetting",
            name="daily_days_notie",
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.PositiveSmallIntegerField(
                    choices=[
                        (0, "Воскресенье"),
                        (1, "Понедельник"),
                        (2, "Вторник"),
                        (3, "Среда"),
                        (4, "Четверг"),
                        (5, "Пятница"),
                        (6, "Суббота"),
                    ]
                ),
                blank=True,
                default=list,
                size=None,
            ),
        ),
    ]
