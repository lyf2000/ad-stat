# Generated by Django 4.2 on 2023-05-29 14:40

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("ad_stat", "0007_companyresponsible"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="company",
            name="responsible",
        ),
        migrations.RenameField(
            model_name="company",
            old_name="responsible_new",
            new_name="responsible",
        ),
    ]
