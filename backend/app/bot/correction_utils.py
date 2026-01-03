from datetime import timedelta
from app.parsing.time_parser import parse_transaction_time
from app.parsing.amount_parser import parse_amount


def resolve_time_window(text: str):
    """
    Return (start_dt, end_dt) window based on natural language time.
    """
    center = parse_transaction_time(text)
    return (
        center - timedelta(hours=3),
        center + timedelta(hours=3),
    )


def parse_edit_instruction(text: str, accounts):
    """
    Extract edit instructions from free text:
    - amount
    - account
    - transaction_at
    """
    result = {}

    # amount
    amt = parse_amount(text)
    if amt:
        result["amount"] = amt

    # account
    text_l = text.lower().replace(" ", "")
    for acc in accounts:
        name = acc.name.lower().replace(" ", "")
        if name in text_l:
            result["account"] = acc
            break

    # time
    if any(k in text.lower() for k in [
        "jam", "pagi", "siang", "sore", "malam", "kemarin"
    ]):
        result["transaction_at"] = parse_transaction_time(text)

    return result
