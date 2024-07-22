# Generated by Django 5.0.2 on 2024-07-16 13:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("production", "0005_boxmodel_layers"),
    ]

    operations = [
        migrations.AlterField(
            model_name="boxmodel",
            name="layers",
            field=models.IntegerField(
                choices=[(3, "3 слоя"), (5, "5 слоев")],
                default=3,
                verbose_name="Количество слоев",
            ),
        ),
    ]
