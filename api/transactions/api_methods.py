import logging
import traceback
from decimal import Decimal

from django.db import IntegrityError
from django.db import transaction as db_transaction
from django.utils import timezone

from api.models import Product, Staff, Transaction, TransactionItem, Venue
from api.realtime.broadcast import broadcast_transaction

logger = logging.getLogger("api")

def create_transaction(data):
    """Store one validated transaction and its line items.

    Args:
        data (dict): the serializer's validated_data.

    Returns:
        Transaction: the created transaction, or None on any failure
        (unknown reference, duplicate, or unexpected error). The reason is
        logged to error.log.
    """
    try:
        with db_transaction.atomic():
            venue = Venue.objects.filter(pk=data["venue_id"]).first()
            if venue is None:
                logger.error("Ingest failed: no venue with id %s", data["venue_id"])
                return None

            staff = Staff.objects.filter(pk=data["staff_id"]).first()
            if staff is None:
                logger.error("Ingest failed: no staff with id %s", data["staff_id"])
                return None

            # Build the line items (also checks every item id exists before save).
            line_items = []
            for line in data["items"]:
                product = Product.objects.filter(pk=line["item_id"]).first()
                if product is None:
                    logger.error("Ingest failed: no item with id %s", line["item_id"])
                    return None
                price = Decimal(str(line["price"]))
                line_items.append(
                    TransactionItem(
                        product=product,
                        quantity=line["quantity"],
                        unit_price=price,
                        line_total=price * line["quantity"],
                    )
                )

            # transaction_number is unique -- a re-sent transaction trips this.
            try:
                txn = Transaction.objects.create(
                    transaction_number=data["transaction_id"],
                    venue=venue,
                    staff=staff,
                    transaction_type=data["transaction_type"],
                    total_amount=data["total_amount"],
                    transaction_time=timezone.now(),  # the payload carries no timestamp
                )
            except IntegrityError:
                logger.error("Ingest failed: transaction %s already exists", data["transaction_id"])
                return None

            for item in line_items:
                item.transaction = txn
            TransactionItem.objects.bulk_create(line_items)

        # Broadcast only after the rows are committed and visible to other workers.
        db_transaction.on_commit(lambda: broadcast_transaction(txn))
        return txn
    except Exception:
        logger.error(traceback.format_exc())
        return None
