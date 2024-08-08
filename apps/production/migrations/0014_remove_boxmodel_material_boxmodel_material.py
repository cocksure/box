# Generated by Django 5.0.2 on 2024-08-08 03:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("info", "0014_alter_boxsize_name"),
        ("production", "0013_alter_typework_options_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="boxmodel",
            name="material",
        ),
        migrations.AddField(
            model_name="boxmodel",
            name="material",
            field=models.ManyToManyField(
                related_name="box_models", to="info.material", verbose_name="Материалы"
            ),
        ),
    ]