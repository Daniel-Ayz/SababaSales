# Generated by Django 5.0.6 on 2024-06-03 09:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0004_basketproduct_store_product_id"),
    ]

    operations = [
        migrations.AddField(
            model_name="basketproduct",
            name="price",
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
    ]
