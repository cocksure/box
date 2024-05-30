# Generated by Django 5.0.2 on 2024-05-28 06:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("production", "0021_alter_processlog_options_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="boxmodel",
            name="grams_per_box",
            field=models.FloatField(
                blank=True, null=True, verbose_name="Граммы на одну коробку"
            ),
        ),
    ]
