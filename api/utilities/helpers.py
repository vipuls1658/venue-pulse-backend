from django.utils import timezone


def money(value):
    """Decimals/None out of the ORM -> plain rounded floats for JSON."""
    return round(float(value or 0), 2)


def start_of_today():
    local_now = timezone.localtime(timezone.now())
    return local_now.replace(hour=0, minute=0, second=0, microsecond=0)
