# Generated by Django 5.0.6 on 2024-07-14 08:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("purchase", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="BidPurchase",
            fields=[
                ("bid_id", models.IntegerField()),
                ("purchase_id", models.AutoField(primary_key=True, serialize=False)),
                ("purchase_date", models.DateTimeField(auto_now_add=True)),
                ("total_price", models.DecimalField(decimal_places=2, max_digits=10)),
                ("total_quantity", models.IntegerField()),
                ("product_name", models.CharField(max_length=100)),
            ],
        ),
    ]
