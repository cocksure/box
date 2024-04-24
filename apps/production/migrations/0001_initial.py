# Generated by Django 5.0.2 on 2024-04-22 09:47

import django.core.validators
import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("info", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="BoxOrder",
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
                    "created_time",
                    models.DateTimeField(default=django.utils.timezone.now),
                ),
                ("updated_time", models.DateTimeField(auto_now=True)),
                ("data", models.DateField()),
                ("customer", models.CharField(blank=True, max_length=100, null=True)),
                (
                    "status",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("Одобрено", "Одобрено"),
                            ("Отклонено", "Отклонено"),
                            ("НОВАЯ", "НОВАЯ"),
                        ],
                        default="НОВАЯ",
                        max_length=20,
                        null=True,
                    ),
                ),
                ("type_order", models.CharField(max_length=100)),
                ("specification", models.CharField(max_length=100)),
                ("date_of_production", models.DateField()),
            ],
            options={
                "ordering": ["-created_time"],
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="BoxOrderDetail",
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
                    "amount",
                    models.DecimalField(
                        decimal_places=2,
                        max_digits=10,
                        validators=[django.core.validators.MinValueValidator(0)],
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Process",
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
                ("name", models.CharField(max_length=100, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name="ProductionOrder",
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
                ("shipping_date", models.DateField()),
                ("amount", models.DecimalField(decimal_places=2, max_digits=10)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("in_progress", "In Progress"),
                            ("completed", "Completed"),
                            ("not_started", "Not Started"),
                        ],
                        default="not_started",
                        max_length=20,
                    ),
                ),
            ],
        ),
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
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="BoxModel",
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
                    "created_time",
                    models.DateTimeField(default=django.utils.timezone.now),
                ),
                ("updated_time", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=100, unique=True)),
                (
                    "box_size",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="box_models_with_size",
                        to="info.boxsize",
                    ),
                ),
                (
                    "box_type",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="box_models_with_type",
                        to="info.boxtype",
                    ),
                ),
            ],
            options={
                "ordering": ["-created_time"],
            },
        ),
    ]
