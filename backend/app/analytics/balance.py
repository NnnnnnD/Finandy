from datetime import date
from sqlalchemy.orm import Session
from app.ledger.calculator import calculate_balance_at
from app.models.accounts import Account


def get_balance_snapshot(db: Session, user_id):
    today = date.today()
    result = []

    accounts = db.query(Account).filter(Account.user_id == user_id).all()

    for acc in accounts:
        saldo = calculate_balance_at(db, acc.id, today)
        if saldo > 0:
            result.append({
                "account": acc.name,
                "is_primary": acc.is_primary,
                "balance": saldo,
            })

    return result
