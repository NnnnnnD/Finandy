from datetime import datetime, timedelta
import re

TIME_BUCKETS = {
    "pagi": (6, 9),
    "siang": (11, 14),
    "sore": (15, 17),
    "malam": (18, 22),
}


def parse_transaction_time(text: str) -> datetime:
    now = datetime.now()
    text = text.lower()

    base_date = now.date()
    if "kemarin" in text:
        base_date -= timedelta(days=1)

    m = re.search(r"jam\s*(\d{1,2})", text)
    if m:
        return datetime.combine(base_date, datetime.min.time()).replace(
            hour=int(m.group(1))
        )

    for k, (a, b) in TIME_BUCKETS.items():
        if k in text:
            return datetime.combine(
                base_date,
                datetime.min.time()
            ).replace(hour=(a + b) // 2)

    return now
