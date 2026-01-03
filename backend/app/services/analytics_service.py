from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date, timedelta

from app.models.transactions import Transaction
from app.models.accounts import Account


# -------------------------
# Monthly Expense
# -------------------------
def monthly_expense(db: Session, user_id: str):
    today = date.today()
    start = today.replace(day=1)

    total = (
        db.query(func.sum(Transaction.amount))
        .join(Account, Transaction.account_id == Account.id)
        .filter(
            Account.user_id == user_id,
            Transaction.type == "expense",
            Transaction.transaction_at >= start,
        )
        .scalar()
    )

    return total or 0


# -------------------------
# Last Transaction
# -------------------------
def last_transaction(db: Session, user_id: str):
    tx = (
        db.query(Transaction)
        .join(Account, Transaction.account_id == Account.id)
        .filter(Account.user_id == user_id)
        .order_by(Transaction.transaction_at.desc())
        .first()
    )

    if not tx:
        return None

    return {
        "text": tx.description,
        "amount": tx.amount,
        "at": tx.transaction_at,
    }


# -------------------------
# Spending Trend
# -------------------------
def spending_trend(db: Session, user_id: str, range: str):
    days = 30 if range == "month" else 7
    start = date.today() - timedelta(days=days)

    rows = (
        db.query(
            func.date(Transaction.transaction_at).label("day"),
            func.sum(Transaction.amount).label("total"),
        )
        .join(Account)
        .filter(
            Account.user_id == user_id,
            Transaction.type == "expense",
            Transaction.transaction_at >= start,
        )
        .group_by("day")
        .order_by("day")
        .all()
    )

    return [{"date": r.day, "amount": r.total} for r in rows]


# -------------------------
# Habit Analysis
# -------------------------
def habit_analysis(db: Session, user_id: str):
    rows = (
        db.query(
            Transaction.description,
            func.count(Transaction.id).label("cnt"),
        )
        .join(Account)
        .filter(Account.user_id == user_id)
        .group_by(Transaction.description)
        .order_by(func.count(Transaction.id).desc())
        .limit(5)
        .all()
    )

    return [
        {"label": r.description, "count": r.cnt}
        for r in rows
    ]


# -------------------------
# Insight Engine
# -------------------------
def insight_summary(db: Session, user_id: str):
    habits = habit_analysis(db, user_id)

    insights = []

    for h in habits:
        if h["count"] >= 10:
            insights.append(
                f"⚠️ '{h['label']}' sering muncul ({h['count']}x bulan ini)"
            )

    if not insights:
        insights.append("👍 Pola pengeluaran kamu masih aman")

    return insights
