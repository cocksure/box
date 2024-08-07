# Generated by Django 5.0.2 on 2024-08-08 10:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("info", "0014_alter_boxsize_name"),
    ]

    operations = [
        migrations.AddField(
            model_name="material",
            name="format",
            field=models.IntegerField(
                blank=True,
                choices=[
                    (90, "90"),
                    (95, "95"),
                    (100, "100"),
                    (105, "105"),
                    (110, "110"),
                    (115, "115"),
                    (120, "120"),
                    (125, "125"),
                    (130, "130"),
                    (135, "135"),
                    (140, "140"),
                    (145, "145"),
                    (150, "150"),
                    (155, "155"),
                    (160, "160"),
                    (165, "165"),
                    (170, "170"),
                    (175, "175"),
                ],
                default=90,
                null=True,
                verbose_name="Формат",
            ),
        ),
    ]
