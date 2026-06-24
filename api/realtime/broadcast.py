"""Send a live "a transaction just happened" message to every open dashboard."""

import logging

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from api.constants import DASHBOARD_GROUP

logger = logging.getLogger("api")


def broadcast_transaction(txn):
    """Notify all open dashboards that a new transaction was saved."""
    layer = get_channel_layer()
    if layer is None:
        return

    # The small bit of info each dashboard needs to refresh itself.
    event = {
        "event": "transaction_created",
        "venue_id": txn.venue_id,
        "transaction_id": txn.transaction_number,
        "total_amount": float(txn.total_amount),
    }

    try:
        async_to_sync(layer.group_send)(
            DASHBOARD_GROUP, {"type": "transaction.created", "payload": event}
        )
    except Exception:
        # If the notification fails, never undo the saved transaction.
        logger.error("Failed to broadcast transaction event", exc_info=True)
