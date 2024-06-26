# Generated by Django 5.0.2 on 2024-05-31 05:08

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Incoming",
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
                ("data", models.DateField(verbose_name="Дата")),
                (
                    "invoice",
                    models.CharField(
                        blank=True, max_length=150, null=True, verbose_name="Накладная"
                    ),
                ),
                (
                    "contract_number",
                    models.CharField(
                        blank=True,
                        max_length=150,
                        null=True,
                        verbose_name="Номер контракта",
                    ),
                ),
                (
                    "note",
                    models.CharField(
                        blank=True, max_length=250, null=True, verbose_name="Примечание"
                    ),
                ),
                (
                    "incoming_type",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("Перемещение", "Перемещение"),
                            ("По накладной", "По накладной"),
                        ],
                        max_length=150,
                        null=True,
                        verbose_name="Тип поступления",
                    ),
                ),
            ],
            options={
                "verbose_name": "Приход",
                "verbose_name_plural": "Приходы",
            },
        ),
        migrations.CreateModel(
            name="IncomingMaterial",
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
                        decimal_places=2, max_digits=10, verbose_name="Количество"
                    ),
                ),
                (
                    "material_party",
                    models.CharField(
                        blank=True,
                        max_length=100,
                        null=True,
                        verbose_name="Партия материала",
                    ),
                ),
                (
                    "comment",
                    models.TextField(
                        blank=True,
                        max_length=1000,
                        null=True,
                        verbose_name="Комментарий",
                    ),
                ),
            ],
            options={
                "verbose_name": "Материал прихода",
                "verbose_name_plural": "Материалы прихода",
            },
        ),
        migrations.CreateModel(
            name="Outgoing",
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
                (
                    "code",
                    models.CharField(
                        editable=False, max_length=10, unique=True, verbose_name="Код"
                    ),
                ),
                ("data", models.DateField(verbose_name="Дата")),
                (
                    "outgoing_type",
                    models.CharField(
                        choices=[
                            ("расход", "Расход"),
                            ("продажа", "Продажа"),
                            ("перемешения", "Перемещение"),
                        ],
                        default="перемешения",
                        max_length=20,
                        verbose_name="Тип исхода",
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("Принят", "Принят"),
                            ("Отклонен", "Отклонен"),
                            ("В ожидании", "В ожидании"),
                        ],
                        default="В ожидании",
                        max_length=20,
                        null=True,
                        verbose_name="Статус",
                    ),
                ),
                (
                    "note",
                    models.CharField(
                        blank=True, max_length=250, null=True, verbose_name="Примечание"
                    ),
                ),
            ],
            options={
                "verbose_name": "Расход",
                "verbose_name_plural": "Расходы",
            },
        ),
        migrations.CreateModel(
            name="OutgoingMaterial",
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
                        decimal_places=2, max_digits=10, verbose_name="Количество"
                    ),
                ),
                (
                    "material_party",
                    models.CharField(
                        blank=True,
                        max_length=100,
                        null=True,
                        verbose_name="Партия материала",
                    ),
                ),
                (
                    "comment",
                    models.TextField(
                        blank=True,
                        max_length=1000,
                        null=True,
                        verbose_name="Комментарий",
                    ),
                ),
            ],
            options={
                "verbose_name": "Материал расхода",
                "verbose_name_plural": "Материалы расхода",
            },
        ),
        migrations.CreateModel(
            name="Stock",
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
                ("amount", models.IntegerField(default=0, verbose_name="Количество")),
            ],
            options={
                "verbose_name": "Остаток на складе",
                "verbose_name_plural": "Остатки на складе",
            },
        ),
    ]
