

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("users", "__first__"),
    ]

    operations = [
        migrations.CreateModel(
            name="DeliveryMethod",
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
                ("address", models.CharField(max_length=255)),
                ("city", models.CharField(max_length=100)),
                ("country", models.CharField(max_length=100)),
                ("zip", models.CharField(max_length=10)),
                ("name", models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name="HistoryBasket",
            fields=[
                ("basket_id", models.AutoField(primary_key=True, serialize=False)),
                ("store_id", models.IntegerField()),
                ("total_price", models.FloatField()),
                ("total_quantity", models.IntegerField()),
                ("discount", models.FloatField()),
            ],
        ),
        migrations.CreateModel(
            name="PaymentMethod",
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
                ("holder", models.CharField(max_length=100)),
                ("holder_identification_number", models.IntegerField()),
                ("currency", models.CharField(max_length=10)),
                ("credit_card_number", models.CharField(max_length=16)),
                ("expiration_date", models.DateField()),
                ("security_code", models.CharField(max_length=3)),
                ("total_price", models.DecimalField(decimal_places=2, max_digits=10)),
            ],
        ),
        migrations.CreateModel(
            name="HistoryBasketProduct",
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
                ("quantity", models.IntegerField()),
                ("name", models.CharField(default="product", max_length=100)),
                ("initial_price", models.FloatField()),
                (
                    "history_basket",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="products",
                        to="purchase.historybasket",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Purchase",
            fields=[
                ("purchase_id", models.AutoField(primary_key=True, serialize=False)),
                ("purchase_date", models.DateTimeField(auto_now_add=True)),
                ("total_price", models.DecimalField(decimal_places=2, max_digits=10)),
                ("total_quantity", models.IntegerField()),
                (
                    "cart",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="users.cart"
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="historybasket",
            name="purchase",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="purchase.purchase"
            ),
        ),
    ]
