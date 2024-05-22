# Generated by Django 5.0.2 on 2024-05-22 06:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("production", "0016_productionorder_code"),
    ]

    operations = [
        migrations.AlterField(
            model_name="productionorder",
            name="status",
            field=models.CharField(
                blank=True,
                choices=[
                    ("in_progress", "В процессе"),
                    ("completed", "Закончен"),
                    ("not_started", "Новый"),
                ],
                default="not_started",
                max_length=20,
                null=True,
                verbose_name="Статус",
            ),
        ),
    ]
