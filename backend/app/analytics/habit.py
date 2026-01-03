# app/analytics/habit.py
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.transactions import Transaction
from app.models.accounts import Account


def get_time_habit(db: Session, user_id):
    rows = (
        db.query(
            func.extract("hour", Transaction.transaction_at).label("hour"),
            func.count(Transaction.id)
        )
        .join(Account, Transaction.account_id == Account.id)
        .filter(Account.user_id == user_id)
        .group_by("hour")
        .order_by(func.count(Transaction.id).desc())
        .all()
    )

    return [{"hour": int(h), "count": c} for h, c in rows]

def get_repeated_transactions(db: Session, user_id):
    rows = (
        db.query(
            Transaction.description,
            func.count(Transaction.id).label("freq"),
        )
        .join(Account, Transaction.account_id == Account.id)
        .filter(Account.user_id == user_id)
        .group_by(Transaction.description)
        .having(func.count(Transaction.id) >= 3)
        .order_by(func.count(Transaction.id).desc())
        .all()
    )

    return [
        {"description": desc, "count": freq}
        for desc, freq in rows
    ]
