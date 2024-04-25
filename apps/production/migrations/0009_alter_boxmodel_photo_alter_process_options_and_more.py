# Generated by Django 5.0.2 on 2024-04-25 08:40

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("production", "0008_uploadimage_alter_boxmodel_photo"),
    ]

    operations = [
        migrations.AlterField(
            model_name="boxmodel",
            name="photo",
            field=models.ImageField(
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
        migrations.AlterModelOptions(
            name="process",
            options={
                "verbose_name": "Загруженное изображение",
                "verbose_name_plural": "Загруженные изображения",
            },
        ),
        migrations.DeleteModel(
            name="UploadImage",
        ),
    ]
