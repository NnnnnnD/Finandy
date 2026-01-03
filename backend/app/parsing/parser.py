from app.parsing.amount_parser import parse_amount
from app.parsing.classifier import classify_transaction
from app.parsing.time_parser import parse_transaction_time


def parse_transaction_text(text: str, *, user_accounts):
    amount = parse_amount(text)
    if amount is None:
        raise ValueError("Amount not found")

    clf = classify_transaction(text)
    tx_time = parse_transaction_time(text)

    return {
        "amount": amount,
        "classification": clf,
        "transaction_at": tx_time,
        "raw_text": text,
    }
