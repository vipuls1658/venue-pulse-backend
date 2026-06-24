class TransactionType:
    """The single source of truth for these strings -- the model's choices and the
    analytics filters both read from here, so adding a type is a one-line change.
    """

    SALE = "SALE"
    VOID = "VOID"
    REFUND = "REFUND"

    CHOICES = [
        (SALE, "Sale"),
        (VOID, "Void"),
        (REFUND, "Refund"),
    ]


class StatusCodes:
    """Named HTTP statuses so views read StatusCodes.get("OK") instead of
    sprinkling raw numbers around. One place to look up what we return."""

    _CODES = {
        "OK": 200,
        "CREATED": 201,
        "BAD_REQUEST": 400,
        "UNAUTHORIZED": 401,
        "NOT_FOUND": 404,
        "SERVER_ERROR": 500,
    }

    @classmethod
    def get(cls, name):
        return cls._CODES[name]

RECENT_WINDOW_MINUTES = 60
BASELINE_WINDOW_MINUTES = 60
SALES_DROP_RATIO = 0.5
SALES_DROP_MIN_BASELINE = 500.0 

VOID_REFUND_SPIKE_RATIO = 0.3
VOID_REFUND_MIN_SALES = 12

TOP_ITEMS_LIMIT = 10
DRILL_DOWN_HOURS = 12
BROADCAST_MIN_INTERVAL = 1.0
DASHBOARD_GROUP = "dashboard"
