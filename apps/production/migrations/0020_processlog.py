# Generated by Django 5.0.2 on 2024-05-22 11:48

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("production", "0019_process_queue"),
    ]

    operations = [
        migrations.CreateModel(
            name="ProcessLog",
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
                    "timestamp",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="Временная метка"
                    ),
                ),
                (
                    "process",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="production.process",
                        verbose_name="Процесс",
                    ),
                ),
                (
                    "production_order",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="process_logs",
                        to="production.productionorder",
                        verbose_name="Заказ на производство",
                    ),
                ),
            ],
            options={
                "verbose_name": "Учет процесса",
            },
        ),
    ]
