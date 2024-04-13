# Generated by Django 5.0.2 on 2024-03-26 06:23

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
                ("created_time", models.DateTimeField(auto_now_add=True, null=True)),
                ("updated_time", models.DateTimeField(auto_now=True)),
                ("data", models.DateField()),
                ("invoice", models.CharField(blank=True, max_length=150, null=True)),
                (
                    "contract_number",
                    models.CharField(blank=True, max_length=150, null=True),
                ),
                ("note", models.CharField(blank=True, max_length=250, null=True)),
                (
                    "incoming_type",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("Перемешения", "Перемешения"),
                            ("По накладной", "По накладной"),
                        ],
                        max_length=150,
                        null=True,
                    ),
                ),
            ],
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
                ("amount", models.DecimalField(decimal_places=2, max_digits=10)),
                (
                    "material_party",
                    models.CharField(blank=True, max_length=100, null=True),
                ),
                ("comment", models.TextField(blank=True, max_length=1000, null=True)),
            ],
        ),
        migrations.CreateModel(
            name="Outgoing",
            fields=[
                ("created_time", models.DateTimeField(auto_now_add=True, null=True)),
                ("updated_time", models.DateTimeField(auto_now=True)),
                ("code", models.CharField(editable=False, max_length=10, unique=True)),
                ("data", models.DateField()),
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
                    ),
                ),
                ("note", models.CharField(blank=True, max_length=250, null=True)),
                ("id", models.AutoField(primary_key=True, serialize=False)),
            ],
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
                ("amount", models.DecimalField(decimal_places=2, max_digits=10)),
                (
                    "material_party",
                    models.CharField(blank=True, max_length=100, null=True),
                ),
                ("comment", models.TextField(blank=True, max_length=1000, null=True)),
            ],
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
                ("amount", models.IntegerField(default=0)),
            ],
        ),
    ]
