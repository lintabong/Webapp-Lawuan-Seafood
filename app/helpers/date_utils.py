
from datetime import datetime, timezone, timedelta

GMT7 = timezone(timedelta(hours=7))

def convert_local_to_gmt(value):
    if value is None:
        return datetime.now(timezone.utc)

    if isinstance(value, datetime):
        if value.tzinfo is None:
            value = value.replace(tzinfo=GMT7)
        return value.astimezone(timezone.utc)

    if isinstance(value, str):
        dt = datetime.fromisoformat(value)
        dt = dt.replace(tzinfo=GMT7)
        return dt.astimezone(timezone.utc)

    raise ValueError("Invalid date format")

def create_now_gmt():
    return datetime.now(timezone.utc)
