import logging
import traceback
from datetime import timedelta

from django.db.models import Count, Q, Sum
from django.utils import timezone

from api import constants
from api.constants import TransactionType
from api.models import Transaction
from api.utilities.helpers import money

logger = logging.getLogger("api")

SALE = TransactionType.SALE
VOID = TransactionType.VOID
REFUND = TransactionType.REFUND


def detect_alerts(now=None):
    """
    Checks all venues and finds unusual transaction activity. It basically compares current hour data with previous hour and returns sales drop, refund spike and void spike alerts.
    """
    try:
        # here we are comparing two windows one is recent = last hour and other baseline = the hour before it.
        now = now or timezone.now()
        recent_start = now - timedelta(minutes=constants.RECENT_WINDOW_MINUTES)
        baseline_start = recent_start - timedelta(minutes=constants.BASELINE_WINDOW_MINUTES)

        # One query per-venue totals for both windows (sums for money and counts for spikes).
        rows = (
            Transaction.objects
            .filter(transaction_time__gte=baseline_start, transaction_time__lt=now)
            .values("venue_id", "venue__venue_name")
            .annotate(
                recent_sales=Sum("total_amount", filter=Q(transaction_type=SALE, transaction_time__gte=recent_start)),
                recent_refunds=Sum("total_amount", filter=Q(transaction_type=REFUND, transaction_time__gte=recent_start)),
                recent_sale_count=Count("id", filter=Q(transaction_type=SALE, transaction_time__gte=recent_start)),
                recent_refund_count=Count("id", filter=Q(transaction_type=REFUND, transaction_time__gte=recent_start)),
                recent_void_count=Count("id", filter=Q(transaction_type=VOID, transaction_time__gte=recent_start)),
                base_sales=Sum("total_amount", filter=Q(transaction_type=SALE, transaction_time__gte=baseline_start, transaction_time__lt=recent_start)),
                base_refunds=Sum("total_amount", filter=Q(transaction_type=REFUND, transaction_time__gte=baseline_start, transaction_time__lt=recent_start)),
            )
        )

    except Exception:
        # Query/setup failure means no alerts can be computed: log and re-raise for the view layer.
        logger.error("Error fetching transactions\n%s", traceback.format_exc())
        raise

    sales_drop_alerts, refund_alerts, void_alerts = [], [], []

    for row in rows:
        # One bad row shouldn't blank the whole board: log it and keep scanning the rest.
        try:
            venue_id = row["venue_id"]
            venue_name = row["venue__venue_name"]
            sale_count = row["recent_sale_count"]

            # Net sales = sales minus refunds, for both windows (None -> 0 via money()).
            recent_net = money(row["recent_sales"]) - money(row["recent_refunds"])
            base_net = money(row["base_sales"]) - money(row["base_refunds"])

            # Sales drop: only for venues busy enough to judge, flag a recent net at/under the ratio.
            if base_net >= constants.SALES_DROP_MIN_BASELINE and recent_net <= base_net * constants.SALES_DROP_RATIO:
                sales_drop_alerts.append({
                    "venue_id": venue_id,
                    "venue_name": venue_name,
                    "drop_percentage": round((1 - recent_net / base_net) * 100)
                })

            # Refund/void spikes share the same minimum-sales floor before either can fire.
            if sale_count >= constants.VOID_REFUND_MIN_SALES:
                # Refund spike: refunds exceed the allowed fraction of this hour's sales.
                if row["recent_refund_count"] > sale_count * constants.VOID_REFUND_SPIKE_RATIO:
                    refund_alerts.append({
                        "venue_id": venue_id,
                        "venue_name": venue_name,
                        "refund_count": row["recent_refund_count"]
                    })

                # Void spike: voids exceed the allowed fraction of this hour's sales.
                if row["recent_void_count"] > sale_count * constants.VOID_REFUND_SPIKE_RATIO:
                    void_alerts.append({
                        "venue_id": venue_id,
                        "venue_name": venue_name,
                        "void_count": row["recent_void_count"]
                    })

        except Exception:
            logger.error("Skipping venue %s\n%s", row.get("venue_id"), traceback.format_exc())

    return {
        "sales_drop_alerts": sales_drop_alerts,
        "refund_alerts": refund_alerts,
        "void_alerts": void_alerts,
    }