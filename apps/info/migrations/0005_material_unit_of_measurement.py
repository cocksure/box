# Generated by Django 5.0.2 on 2024-04-22 12:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("info", "0004_remove_material_unit_of_measurement"),
    ]

    operations = [
        migrations.AddField(
            model_name="material",
            name="unit_of_measurement",
            field=models.CharField(
                choices=[
                    ("sht", "шт"),
                    ("sm", "см"),
                    ("mm", "мм"),
                    ("kg", "кг"),
                    ("litr", "л"),
                ],
                default=None,
                max_length=10,
                verbose_name="Единица измерения",
            ),
        ),
    ]