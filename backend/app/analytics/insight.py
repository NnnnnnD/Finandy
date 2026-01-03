from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.transactions import Transaction
from app.models.accounts import Account


def spending_trend(db: Session, user_id):
    now = datetime.now()

    this_week = now - timedelta(days=7)
    last_week = now - timedelta(days=14)

    def total(start, end):
        return (
            db.query(func.sum(Transaction.amount))
            .join(Account, Transaction.account_id == Account.id)
            .filter(
                Account.user_id == user_id,
                Transaction.type == "expense",
                Transaction.transaction_at.between(start, end),
            )
            .scalar() or 0
        )

    current = total(this_week, now)
    previous = total(last_week, this_week)

    if previous == 0:
        return None

    delta = (current - previous) / previous * 100

    if delta > 20:
        return {
            "type": "warning",
            "message": f"Pengeluaran naik {delta:.0f}% dibanding minggu lalu"
        }

    return {
        "type": "info",
        "message": "Pengeluaran kamu stabil 👍"
    }
