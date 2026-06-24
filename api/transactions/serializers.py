from decimal import Decimal

from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from api.constants import TransactionType
from api.models import Transaction

ZERO = Decimal("0")


class LineItemSerializer(serializers.Serializer):
    """One line on a transaction. ``item_id`` is a Product primary key."""

    item_id = serializers.IntegerField(min_value=1)
    quantity = serializers.IntegerField(min_value=1)
    price = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=ZERO)


class TransactionCreateSerializer(serializers.Serializer):
    """Validates an incoming POS transaction.

    ``venue_id`` and ``staff_id`` are primary keys that must already exist; the
    service layer resolves them. ``transaction_id`` is the venue's own reference
    and is stored as ``transaction_number`` (unique, for idempotency).
    """

    venue_id = serializers.IntegerField(min_value=1)
    transaction_id = serializers.CharField(max_length=64)
    transaction_type = serializers.ChoiceField(choices=Transaction.TYPE_CHOICES)
    total_amount = serializers.DecimalField(max_digits=12, decimal_places=2, min_value=ZERO)
    staff_id = serializers.IntegerField(min_value=1)
    items = LineItemSerializer(many=True, allow_empty=False)

    def validate(self, attrs):
        # A sale with no money is almost always a malformed feed.
        if attrs["transaction_type"] == TransactionType.SALE and attrs["total_amount"] <= 0:
            raise serializers.ValidationError(_("transaction.sale_positive_total"))
        return attrs
