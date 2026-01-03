import re
from datetime import date, timedelta
from typing import Optional


RELATIVE_KEYWORDS = {
    "hari": "days",
    "minggu": "weeks",
}


def parse_date(text: str, *, today: Optional[date] = None) -> date:
    """
    Priority:
    1. Explicit date (12/12, 12-12-2025)
    2. Relative (kemarin, 2 hari lalu)
    3. Default: today
    """

    if not today:
        today = date.today()

    text = text.lower()

    # 1️⃣ explicit date
    explicit_pattern = re.compile(
        r"\b(?P<day>\d{1,2})[/-](?P<month>\d{1,2})(?:[/-](?P<year>\d{2,4}))?\b"
    )

    match = explicit_pattern.search(text)
    if match:
        day = int(match.group("day"))
        month = int(match.group("month"))
        year = match.group("year")

        if year:
            year = int(year)
            if year < 100:
                year += 2000
        else:
            year = today.year

        try:
            parsed = date(year, month, day)
            if parsed <= today:
                return parsed
        except ValueError:
            pass

    # 2️⃣ relative keywords
    if "kemarin" in text:
        return today - timedelta(days=1)

    if "tadi" in text:
        return today

    # 3️⃣ relative numeric
    relative_pattern = re.compile(
        r"\b(?P<number>\d+)\s*(?P<unit>hari|minggu)\s*lalu\b"
    )

    match = relative_pattern.search(text)
    if match:
        number = int(match.group("number"))
        unit = match.group("unit")
        delta = timedelta(**{RELATIVE_KEYWORDS[unit]: number})
        return today - delta

    return today
