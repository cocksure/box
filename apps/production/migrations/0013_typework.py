# Generated by Django 5.0.2 on 2024-05-08 10:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("production", "0012_alter_boxmodel_additional_properties_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="TypeWork",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        max_length=100, unique=True, verbose_name="Тип работы"
                    ),
                ),
                (
                    "process",
                    models.ManyToManyField(
                        to="production.process", verbose_name="Процесс"
                    ),
                ),
            ],
            options={
                "verbose_name": "Тип работы",
                "verbose_name_plural": "Типы работы",
            },
        ),
    ]