# Generated by Django 5.0.2 on 2024-05-08 11:44

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("production", "0013_typework"),
    ]

    operations = [
        migrations.AlterField(
            model_name="productionorder",
            name="shipping_date",
            field=models.DateField(blank=True, null=True, verbose_name="Дата доставки"),
        ),
        migrations.AlterField(
            model_name="productionorder",
            name="status",
            field=models.CharField(
                blank=True,
                choices=[
                    ("in_progress", "In Progress"),
                    ("completed", "Completed"),
                    ("not_started", "Not Started"),
                ],
                default="not_started",
                max_length=20,
                null=True,
                verbose_name="Статус",
            ),
        ),
        migrations.RemoveField(
            model_name="productionorder",
            name="type_of_work",
        ),
        migrations.AddField(
            model_name="productionorder",
            name="type_of_work",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="production.typework",
                verbose_name="Тип Работы",
            ),
        ),
    ]
