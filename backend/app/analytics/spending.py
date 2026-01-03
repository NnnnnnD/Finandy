from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.transactions import Transaction
from app.models.accounts import Account


def get_spending(db: Session, user_id, range_: str):
    now = datetime.now()

    if range_ == "day":
        start = now.replace(hour=0, minute=0, second=0)
    elif range_ == "week":
        start = now - timedelta(days=7)
    else:
        start = now - timedelta(days=30)

    rows = (
        db.query(
            Account.name,
            func.sum(Transaction.amount).label("total")
        )
        .join(Transaction, Transaction.account_id == Account.id)
        .filter(
            Account.user_id == user_id,
            Transaction.type == "expense",
            Transaction.transaction_at >= start,
        )
        .group_by(Account.name)
        .all()
    )

    return [
        {"account": name, "total_spent": int(total)}
        for name, total in rows
    ]
