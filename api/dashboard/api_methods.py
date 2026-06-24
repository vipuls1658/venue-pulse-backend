import logging
import traceback
from datetime import timedelta

from django.db.models import Sum
from django.db.models.functions import TruncHour
from django.utils import timezone

from api import constants
from api.constants import TransactionType
from api.models import Transaction, TransactionItem, Venue
from api.utilities.helpers import money, start_of_today

from .anomalies import detect_alerts

logger = logging.getLogger("api")

SALE = TransactionType.SALE


def venue_sales():
    """Today's sales ranking by venue: [{venue_id, venue_name, total_sales}]."""
    try:
        rows = (
            Transaction.objects.filter(
                transaction_time__gte=start_of_today(), transaction_type=SALE
            )
            .values("venue_id", "venue__venue_name")
            .annotate(total_sales=Sum("total_amount"))
            .order_by("-total_sales")
        )
        data = [
            {
                "venue_id": r["venue_id"],
                "venue_name": r["venue__venue_name"],
                "total_sales": money(r["total_sales"]),
            }
            for r in rows
        ]
        return data
    except Exception:
        logger.error(traceback.format_exc())
        return []


def top_items(venue_id=None, limit=constants.TOP_ITEMS_LIMIT):
    """Top selling items today: [{item_id, item_name, quantity_sold}]."""
    try:
        qs = TransactionItem.objects.filter(
            transaction__transaction_time__gte=start_of_today(),
            transaction__transaction_type=SALE,
        )
        if venue_id is not None:
            qs = qs.filter(transaction__venue_id=venue_id)
        rows = (
            qs.values("product_id", "product__product_name")
            .annotate(quantity_sold=Sum("quantity"))
            .order_by("-quantity_sold")
        )
        # limit=None means "no cap" -- the paginated endpoint slices the full set.
        if limit is not None:
            rows = rows[:limit]
        data = [
            {
                "item_id": r["product_id"],
                "item_name": r["product__product_name"],
                "quantity_sold": r["quantity_sold"],
            }
            for r in rows
        ]
        return data
    except Exception:
        logger.error(traceback.format_exc())
        return []


def alerts():
    """Active alerts grouped by kind (sales drop / refund / void spikes)."""
    try:
        data = detect_alerts()
        return data
    except Exception:
        logger.error(traceback.format_exc())
        return {}


def hourly_sales(venue_id=None):
    """Hourly sales trend for the last DRILL_DOWN_HOURS hours.

    For all venues, or one venue when venue_id is given. Returns
    [{"hour": "09:00", "sales": ...}] with a continuous bar per hour (gaps
    filled with zero) so a chart has no holes.
    """
    try:
        tz = timezone.get_current_timezone()
        span_start = timezone.now() - timedelta(hours=constants.DRILL_DOWN_HOURS)

        qs = Transaction.objects.filter(transaction_time__gte=span_start, transaction_type=SALE)
        if venue_id is not None:
            qs = qs.filter(venue_id=venue_id)
        rows = (
            qs.annotate(bucket=TruncHour("transaction_time", tzinfo=tz))
            .values("bucket")
            .annotate(sales=Sum("total_amount"))
        )
        by_hour = {row["bucket"]: money(row["sales"]) for row in rows}

        series = []
        cursor = timezone.localtime(span_start).replace(minute=0, second=0, microsecond=0)
        end = timezone.localtime(timezone.now()).replace(minute=0, second=0, microsecond=0)
        while cursor <= end:
            series.append({"hour": cursor.strftime("%H:%M"), "sales": by_hour.get(cursor, 0.0)})
            cursor += timedelta(hours=1)
        return series
    except Exception:
        logger.error(traceback.format_exc())
        return []


def venue_detail(venue_id):
    """Detailed view for one venue, or ``None`` if it doesn't exist.

    ``{venue_id, venue_name, total_sales, hourly_sales, top_selling_items}``
    """
    try:
        venue = Venue.objects.filter(pk=venue_id).first()
        if venue is None:
            return None

        total = Transaction.objects.filter(
            venue=venue, transaction_time__gte=start_of_today(), transaction_type=SALE
        ).aggregate(total=Sum("total_amount"))["total"]

        top_selling_items = [
            {"item_name": item["item_name"], "quantity_sold": item["quantity_sold"]}
            for item in top_items(venue_id=venue.id)
        ]

        data = {
            "venue_id": venue.id,
            "venue_name": venue.venue_name,
            "total_sales": money(total),
            "hourly_sales": hourly_sales(venue_id=venue.id),
            "top_selling_items": top_selling_items,
        }
        return data
    except Exception:
        logger.error(traceback.format_exc())
        return None
