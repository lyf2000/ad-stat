# Generated by Django 4.2.3 on 2023-10-21 09:57

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("ad_stat", "0031_alter_notielog_company_alter_notielog_type"),
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
                    (7, "Топ запросов с большим коэффициентом отказов по URL"),
                    (15, "Топ запросов с большим коэффициентом отказов по запросам"),
                    (
                        13,
                        "Отчет топ запросов с большим коэффициентом визитов по поиску",
                    ),
                    (14, "Отчет по поисковым запросам с контекстной рекламы"),
                    (
                        8,
                        "Отчет топ запросов с большим коэффициентом отказов по экранам",
                    ),
                    (
                        9,
                        "Отчет топ запросов с большим коэффициентом отказов по устройствам",
                    ),
                    (
                        10,
                        "Отчет топ запросов с большим коэффициентом отказов по типам устройств",
                    ),
                    (
                        11,
                        "Отчет топ запросов с большим коэффициентом отказов по типам устройств",
                    ),
                    (12, "Отчет по целям и конверсиям за предыдущую неделю"),
                ],
                verbose_name="Тип отчета",
            ),
        ),
    ]
