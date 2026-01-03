import re
from typing import Optional


MULTIPLIERS = {
    "k": 1_000,
    "rb": 1_000,
    "ribu": 1_000,
    "jt": 1_000_000,
    "juta": 1_000_000,
}


def normalize_amount_text(text: str) -> str:
    text = text.lower()

    # remove thousand separators (ID format)
    text = re.sub(r"(?<=\d)[.,](?=\d{3}\b)", "", text)

    # remove commas
    text = text.replace(",", "")

    return text


def parse_amount(text: str) -> Optional[int]:
    """
    Parse amount from free text.
    Returns int rupiah or None.
    """

    text = normalize_amount_text(text)

    # 1️⃣ unit-based: 2.5jt, 25rb, 70k
    pattern_unit = re.compile(
        r"(?P<number>\d+(\.\d+)?)\s*(?P<unit>jt|juta|rb|ribu|k)\b"
    )

    match = pattern_unit.search(text)
    if match:
        number = float(match.group("number"))
        unit = match.group("unit")
        return int(number * MULTIPLIERS[unit])

    # 2️⃣ plain number: 120000
    pattern_plain = re.compile(r"\b\d{4,}\b")
    match = pattern_plain.search(text)
    if match:
        return int(match.group())

    return None
