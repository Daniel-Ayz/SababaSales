# Generated by Django 5.0.6 on 2024-05-18 19:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="basketproduct",
            name="name",
            field=models.CharField(default="product", max_length=100),
        ),
        migrations.AlterField(
            model_name="basketproduct",
            name="id",
            field=models.BigAutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
    ]
