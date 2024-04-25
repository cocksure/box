# Generated by Django 5.0.2 on 2024-04-25 13:56

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("production", "0010_alter_process_options"),
    ]

    operations = [
        migrations.AddField(
            model_name="boxmodel",
            name="additional_properties",
            field=models.IntegerField(
                choices=[
                    (1, "Влагостойкость"),
                    (2, "Устойчивость к воздействию"),
                    (3, "Экологичность"),
                    (4, "Теплоизоляция"),
                    (5, "Антистатические свойства"),
                ],
                default=None,
                verbose_name="Дополнительные свойства",
            ),
        ),
        migrations.AddField(
            model_name="boxmodel",
            name="closure_type",
            field=models.IntegerField(
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
                default=None,
                verbose_name="Тип замыкания",
            ),
        ),
        migrations.AddField(
            model_name="boxmodel",
            name="color",
            field=models.CharField(
                blank=True, max_length=50, null=True, verbose_name="Цвет"
            ),
        ),
        migrations.AddField(
            model_name="boxmodel",
            name="comment",
            field=models.TextField(blank=True, null=True, verbose_name="Комментарий"),
        ),
        migrations.AddField(
            model_name="boxmodel",
            name="max_load",
            field=models.CharField(
                blank=True,
                max_length=50,
                null=True,
                verbose_name="Максимальная нагрузка",
            ),
        ),
        migrations.AlterField(
            model_name="boxmodel",
            name="photo",
            field=models.ImageField(
                default="box_photos/no-image.png",
                upload_to="box_photos",
                validators=[
                    django.core.validators.FileExtensionValidator(
                        allowed_extensions=["jpg", "jpeg", "png", "heic"]
                    )
                ],
                verbose_name="Изображение",
            ),
        ),
    ]