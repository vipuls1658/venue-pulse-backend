import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Venue",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("venue_code", models.SlugField(max_length=50, unique=True)),
                ("venue_name", models.CharField(max_length=255)),
                (
                    "venue_type",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("pub", "Pub"),
                            ("restaurant", "Restaurant"),
                            ("function", "Function space"),
                        ],
                        max_length=50,
                    ),
                ),
                ("city", models.CharField(blank=True, max_length=100)),
            ],
            options={
                "db_table": "venues",
                "ordering": ["venue_code"],
            },
        ),
        migrations.CreateModel(
            name="Product",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("product_code", models.CharField(blank=True, max_length=50)),
                ("product_name", models.CharField(max_length=255)),
                ("current_price", models.DecimalField(decimal_places=2, max_digits=10)),
            ],
            options={
                "db_table": "products",
            },
        ),
        migrations.CreateModel(
            name="Staff",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("staff_code", models.CharField(blank=True, max_length=50)),
                ("staff_name", models.CharField(max_length=255)),
                (
                    "venue",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="staff_members",
                        to="api.venue",
                    ),
                ),
            ],
            options={
                "db_table": "staff_members",
            },
        ),
        migrations.CreateModel(
            name="Transaction",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("transaction_number", models.CharField(max_length=100, unique=True)),
                (
                    "transaction_type",
                    models.CharField(
                        choices=[("SALE", "Sale"), ("VOID", "Void"), ("REFUND", "Refund")],
                        max_length=20,
                    ),
                ),
                ("total_amount", models.DecimalField(decimal_places=2, max_digits=12)),
                ("transaction_time", models.DateTimeField()),
                (
                    "venue",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="transactions",
                        to="api.venue",
                    ),
                ),
                (
                    "staff",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="transactions",
                        to="api.staff",
                    ),
                ),
            ],
            options={
                "db_table": "transactions",
            },
        ),
        migrations.CreateModel(
            name="TransactionItem",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("quantity", models.PositiveIntegerField()),
                ("unit_price", models.DecimalField(decimal_places=2, max_digits=10)),
                ("line_total", models.DecimalField(decimal_places=2, max_digits=12)),
                (
                    "transaction",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="items",
                        to="api.transaction",
                    ),
                ),
                (
                    "product",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="line_items",
                        to="api.product",
                    ),
                ),
            ],
            options={
                "db_table": "transaction_items",
            },
        ),
        migrations.AddIndex(
            model_name="transaction",
            index=models.Index(fields=["venue"], name="idx_transactions_venue"),
        ),
        migrations.AddIndex(
            model_name="transaction",
            index=models.Index(fields=["transaction_time"], name="idx_transactions_time"),
        ),
        migrations.AddIndex(
            model_name="transaction",
            index=models.Index(fields=["transaction_type"], name="idx_transactions_type"),
        ),
        migrations.AddIndex(
            model_name="transactionitem",
            index=models.Index(fields=["product"], name="idx_transaction_items_product"),
        ),
        migrations.AddIndex(
            model_name="transactionitem",
            index=models.Index(fields=["transaction"], name="idx_transaction_items_txn"),
        ),
    ]
