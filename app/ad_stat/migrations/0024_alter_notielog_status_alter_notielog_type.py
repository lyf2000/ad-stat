# Generated by Django 4.2.3 on 2023-07-25 18:41

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("ad_stat", "0023_notielog_type_alter_notielog_result"),
    ]

    operations = [
        migrations.AlterField(
            model_name="notielog",
            name="status",
            field=models.PositiveSmallIntegerField(
                choices=[
                    (0, "Не отправлено"),
                    (1, "Отправлено"),
                    (2, "Ошибка"),
                    (3, "Пустое сообщение"),
                ],
                default=0,
                verbose_name="Статус",
            ),
        ),
        migrations.AlterField(
            model_name="notielog",
            name="type",
            field=models.PositiveSmallIntegerField(
                choices=[
                    (1, "Ежедневная рассылка отчета по статистике"),
                    (2, "Еженедельная рассылка отчета по рекламе"),
                    (3, "Ежедневная рассылка отчета по статистике"),
                ],
                verbose_name="Тип отчета",
            ),
        ),
    ]
