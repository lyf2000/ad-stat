# Generated by Django 4.2.3 on 2023-08-02 09:45

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("ad_stat", "0026_companyuissetting"),
    ]

    operations = [
        migrations.AlterField(
            model_name="notielog",
            name="type",
            field=models.PositiveSmallIntegerField(
                choices=[
                    (1, "Отчет по статистике за вчерашний день"),
                    (2, "Отчет по рекламе за предыдущую неделю"),
                    (3, "Отчет по статистике за предыдущий месяц"),
                    (4, "Создан счет на оплату"),
                    (5, "Напоминание о необходимости оплатить выставленный счет"),
                    (6, "Рассылка баланса"),
                    (7, "Отчет топ запросов с большим коэффициентом отказов"),
                ],
                verbose_name="Тип отчета",
            ),
        ),
    ]
