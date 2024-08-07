# Generated by Django 5.0.2 on 2024-07-20 07:54

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("depo", "0007_alter_outgoingmaterial_production_order"),
        ("production", "0010_remove_productionorder_outgoing_materials_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="outgoing",
            name="production_order",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="outgoings",
                to="production.productionorder",
            ),
        ),
    ]
