# Generated by Django 4.2 on 2023-07-03 13:58

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("users", "0001_initial"),
    ]

    operations = [
        migrations.RenameModel(
            old_name="YandexToken",
            new_name="YandexUser",
        ),
        migrations.RenameField(
            model_name="yandexuser",
            old_name="author",
            new_name="user",
        ),
        migrations.AddField(
            model_name="yandexuser",
            name="email",
            field=models.EmailField(default="chageme@mail.ru", max_length=254, verbose_name="Почта"),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="yandexuser",
            name="first_name",
            field=models.CharField(default="chageme@mail.ru", max_length=128, verbose_name="Имя"),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="yandexuser",
            name="last_name",
            field=models.CharField(default="chageme@mail.ru", max_length=128, verbose_name="Фамилия"),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="yandexuser",
            name="login",
            field=models.CharField(default="changeme", max_length=128, verbose_name="Логин"),
            preserve_default=False,
        ),
    ]
