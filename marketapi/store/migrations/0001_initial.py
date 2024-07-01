

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("contenttypes", "0002_remove_content_type_name"),
    ]

    operations = [
        migrations.CreateModel(
            name="DiscountBase",
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
                ("is_root", models.BooleanField(default=False)),
                (
                    "polymorphic_ctype",
                    models.ForeignKey(
                        editable=False,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="polymorphic_%(app_label)s.%(class)s_set+",
                        to="contenttypes.contenttype",
                    ),
                ),
            ],
            options={
                "abstract": False,
                "base_manager_name": "objects",
            },
        ),
        migrations.CreateModel(
            name="PurchasePolicyBase",
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
                ("is_root", models.BooleanField(default=False)),
                (
                    "polymorphic_ctype",
                    models.ForeignKey(
                        editable=False,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="polymorphic_%(app_label)s.%(class)s_set+",
                        to="contenttypes.contenttype",
                    ),
                ),
            ],
            options={
                "abstract": False,
                "base_manager_name": "objects",
            },
        ),
        migrations.CreateModel(
            name="Role",
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
                ("user_id", models.IntegerField()),
                (
                    "polymorphic_ctype",
                    models.ForeignKey(
                        editable=False,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="polymorphic_%(app_label)s.%(class)s_set+",
                        to="contenttypes.contenttype",
                    ),
                ),
            ],
            options={
                "abstract": False,
                "base_manager_name": "objects",
            },
        ),
        migrations.CreateModel(
            name="Store",
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
                ("name", models.CharField(max_length=255)),
                ("description", models.TextField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("is_active", models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name="SimplePurchasePolicy",
            fields=[
                (
                    "purchasepolicybase_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="store.purchasepolicybase",
                    ),
                ),
            ],
            options={
                "abstract": False,
                "base_manager_name": "objects",
            },
            bases=("store.purchasepolicybase",),
        ),
        migrations.CreateModel(
            name="Condition",
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
                ("applies_to", models.CharField(max_length=255)),
                ("name_of_apply", models.CharField(max_length=255)),
                ("condition", models.CharField(max_length=255)),
                ("value", models.FloatField()),
                (
                    "discount",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="conditions",
                        to="store.discountbase",
                    ),
                ),
                (
                    "purchase_policy",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="conditions",
                        to="store.purchasepolicybase",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Manager",
            fields=[
                (
                    "role_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="store.role",
                    ),
                ),
            ],
            options={
                "abstract": False,
                "base_manager_name": "objects",
            },
            bases=("store.role",),
        ),
        migrations.AddField(
            model_name="role",
            name="store",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="store.store"
            ),
        ),
        migrations.AddField(
            model_name="purchasepolicybase",
            name="store",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="store.store"
            ),
        ),
        migrations.AddField(
            model_name="discountbase",
            name="store",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="store.store"
            ),
        ),
        migrations.CreateModel(
            name="StoreProduct",
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
                ("initial_price", models.FloatField()),
                ("quantity", models.IntegerField()),
                ("name", models.CharField(max_length=255)),
                ("category", models.CharField(max_length=255)),
                ("image_link", models.CharField(blank=True, max_length=255, null=True)),
                (
                    "store",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="store_products",
                        to="store.store",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Bid",
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
                ("price", models.FloatField()),
                ("user_id", models.IntegerField()),
                ("can_purchase", models.BooleanField(default=False)),
                (
                    "accepted_by",
                    models.ManyToManyField(
                        blank=True, related_name="accepted_bids", to="store.role"
                    ),
                ),
                (
                    "store",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="store.store"
                    ),
                ),
                (
                    "product",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="store.storeproduct",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="CompositeDiscount",
            fields=[
                (
                    "discountbase_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="store.discountbase",
                    ),
                ),
                ("combine_function", models.CharField(max_length=50)),
                (
                    "discounts",
                    models.ManyToManyField(
                        related_name="composite_discounts", to="store.discountbase"
                    ),
                ),
            ],
            options={
                "abstract": False,
                "base_manager_name": "objects",
            },
            bases=("store.discountbase",),
        ),
        migrations.CreateModel(
            name="ConditionalDiscount",
            fields=[
                (
                    "discountbase_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="store.discountbase",
                    ),
                ),
                (
                    "discount",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="conditional_discounts",
                        to="store.discountbase",
                    ),
                ),
            ],
            options={
                "abstract": False,
                "base_manager_name": "objects",
            },
            bases=("store.discountbase",),
        ),
        migrations.CreateModel(
            name="SimpleDiscount",
            fields=[
                (
                    "discountbase_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="store.discountbase",
                    ),
                ),
                ("percentage", models.FloatField()),
                ("applicable_categories", models.TextField(blank=True, null=True)),
                (
                    "applicable_products",
                    models.ManyToManyField(
                        related_name="simple_discounts", to="store.storeproduct"
                    ),
                ),
            ],
            options={
                "abstract": False,
                "base_manager_name": "objects",
            },
            bases=("store.discountbase",),
        ),
        migrations.CreateModel(
            name="CompositePurchasePolicy",
            fields=[
                (
                    "purchasepolicybase_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="store.purchasepolicybase",
                    ),
                ),
                ("combine_function", models.CharField(max_length=50)),
                (
                    "policies",
                    models.ManyToManyField(
                        related_name="composite_purchase_policies",
                        to="store.purchasepolicybase",
                    ),
                ),
            ],
            options={
                "abstract": False,
                "base_manager_name": "objects",
            },
            bases=("store.purchasepolicybase",),
        ),
        migrations.CreateModel(
            name="ConditionalPurchasePolicy",
            fields=[
                (
                    "purchasepolicybase_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="store.purchasepolicybase",
                    ),
                ),
                (
                    "condition",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="condition_policies",
                        to="store.purchasepolicybase",
                    ),
                ),
                (
                    "restriction",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="restriction_policies",
                        to="store.purchasepolicybase",
                    ),
                ),
            ],
            options={
                "abstract": False,
                "base_manager_name": "objects",
            },
            bases=("store.purchasepolicybase",),
        ),
        migrations.CreateModel(
            name="ManagerPermission",
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
                ("can_add_product", models.BooleanField(default=False)),
                ("can_edit_product", models.BooleanField(default=False)),
                ("can_delete_product", models.BooleanField(default=False)),
                ("can_add_discount_policy", models.BooleanField(default=False)),
                ("can_add_purchase_policy", models.BooleanField(default=False)),
                ("can_remove_discount_policy", models.BooleanField(default=False)),
                ("can_remove_purchase_policy", models.BooleanField(default=False)),
                ("can_decide_on_bid", models.BooleanField(default=False)),
                (
                    "manager",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="manager_permissions",
                        to="store.manager",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Owner",
            fields=[
                (
                    "role_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="store.role",
                    ),
                ),
                ("is_founder", models.BooleanField(default=False)),
                (
                    "assigned_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="assigned_owners",
                        to="store.owner",
                    ),
                ),
            ],
            options={
                "abstract": False,
                "base_manager_name": "objects",
            },
            bases=("store.role",),
        ),
        migrations.AddField(
            model_name="manager",
            name="assigned_by",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="assigned_managers",
                to="store.owner",
            ),
        ),
    ]
