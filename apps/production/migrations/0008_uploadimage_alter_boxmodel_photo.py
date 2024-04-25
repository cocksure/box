# Generated by Django 5.0.2 on 2024-04-25 07:33

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("production", "0007_alter_boxorder_specification"),
    ]

    operations = [
        migrations.CreateModel(
            name="UploadImage",
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
                    "photo",
                    models.ImageField(
                        default="no-image.png",
                        upload_to="box_photos/",
                        validators=[
                            django.core.validators.FileExtensionValidator(
                                allowed_extensions=["jpg", "jpeg", "png", "heic"]
                            )
                        ],
                        verbose_name="Изображение",
                    ),
                ),
            ],
            options={
                "verbose_name": "Загруженное изображение",
                "verbose_name_plural": "Загруженные изображения",
            },
        ),
        migrations.AlterField(
            model_name="boxmodel",
            name="photo",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="production.uploadimage",
                verbose_name="Изображение",
            ),
        ),
    ]