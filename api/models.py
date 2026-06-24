from django.db import models

from api.constants import TransactionType
from api.utilities.base import TimeStampedModel


# A venue we track sales for, like a pub or restaurant.
class Venue(TimeStampedModel):
    KIND_CHOICES = [
        ("pub", "Pub"),
        ("restaurant", "Restaurant"),
        ("function", "Function space"),
    ]

    venue_code = models.SlugField(max_length=50, unique=True)
    venue_name = models.CharField(max_length=255)
    venue_type = models.CharField(max_length=50, choices=KIND_CHOICES, blank=True)
    city = models.CharField(max_length=100, blank=True)

    class Meta:
        db_table = "venues"
        ordering = ["venue_code"]

    def __str__(self):
        return f"{self.venue_name} ({self.venue_code})"


# A person who rings up sales at a venue.
class Staff(TimeStampedModel):
    venue = models.ForeignKey(Venue, on_delete=models.CASCADE, related_name="staff_members")
    staff_code = models.CharField(max_length=50, blank=True)
    staff_name = models.CharField(max_length=255)

    class Meta:
        db_table = "staff_members"

    def __str__(self):
        return f"{self.staff_name} ({self.staff_code})"


# A product that can appear on a transaction line.
class Product(TimeStampedModel):
    product_code = models.CharField(max_length=50, blank=True)
    product_name = models.CharField(max_length=255)
    current_price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        db_table = "products"

    def __str__(self):
        return f"{self.product_name} ({self.product_code})"


# A single sale, void or refund that came in from a venue's POS.
class Transaction(TimeStampedModel):
    TYPE_CHOICES = TransactionType.CHOICES

    transaction_number = models.CharField(max_length=100, unique=True)
    venue = models.ForeignKey(Venue, on_delete=models.PROTECT, related_name="transactions")
    staff = models.ForeignKey(Staff, on_delete=models.PROTECT, related_name="transactions")
    transaction_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    transaction_time = models.DateTimeField()

    class Meta:
        db_table = "transactions"
        indexes = [
            models.Index(fields=["venue"], name="idx_transactions_venue"),
            models.Index(fields=["transaction_time"], name="idx_transactions_time"),
            models.Index(fields=["transaction_type"], name="idx_transactions_type"),
        ]

    def __str__(self):
        return f"{self.transaction_type} {self.transaction_number} @ {self.venue.venue_code}"


# One product line on a transaction.
class TransactionItem(models.Model):
    transaction = models.ForeignKey(
        Transaction, on_delete=models.CASCADE, related_name="items"
    )
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name="line_items")
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    line_total = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        db_table = "transaction_items"
        indexes = [
            models.Index(fields=["product"], name="idx_transaction_items_product"),
            models.Index(fields=["transaction"], name="idx_transaction_items_txn"),
        ]

    def __str__(self):
        return f"{self.quantity}x {self.product.product_name}"
