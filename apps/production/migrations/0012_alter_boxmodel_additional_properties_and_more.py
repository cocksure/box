# Generated by Django 5.0.2 on 2024-04-29 08:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        (
            "production",
            "0011_boxmodel_additional_properties_boxmodel_closure_type_and_more",
        ),
    ]

    operations = [
        migrations.AlterField(
            model_name="boxmodel",
            name="additional_properties",
            field=models.IntegerField(
                blank=True,
                choices=[
                    (1, "Влагостойкость"),
                    (2, "Устойчивость к воздействию"),
                    (3, "Экологичность"),
                    (4, "Теплоизоляция"),
                    (5, "Антистатические свойства"),
                ],
                null=True,
                verbose_name="Дополнительные свойства",
            ),
        ),
        migrations.AlterField(
            model_name="boxmodel",
            name="closure_type",
            field=models.IntegerField(
                blank=True,
                choices=[
                    (1, "Склейка"),
                    (2, "Клапаны"),
                    (3, "Автозамок"),
                    (4, "Скобы"),
                    (5, "Ленты или бандероли"),
                    (6, "Крючки или зажимы"),
                    (7, "Вкладыш"),
                    (8, "Магниты"),
                ],
                null=True,
                verbose_name="Тип замыкания",
            ),
        ),
    ]
