# app/api/analytics.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import timedelta, date

from app.core.database import get_db
from app.models.transactions import Transaction
from app.models.accounts import Account

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/spending")
def spending_analytics(
    user_id: str,
    days: int = 7,
    db: Session = Depends(get_db),
):
    since = date.today() - timedelta(days=days)

    rows = (
        db.query(
            func.date(Transaction.transaction_at).label("day"),
            func.sum(Transaction.amount).label("total"),
        )
        .join(Account, Transaction.account_id == Account.id)
        .filter(
            Account.user_id == user_id,
            Transaction.type == "expense",
            Transaction.transaction_at >= since,
        )
        .group_by("day")
        .order_by("day")
        .all()
    )

    return {
        "period_days": days,
        "by_day": [
            {"date": str(r.day), "amount": int(r.total)}
            for r in rows
        ],
    }


@router.get("/habits")
def habit_insights(
    user_id: str,
    db: Session = Depends(get_db),
):
    """
    Simple habit insight (placeholder for ML)
    """
    insights = []

    insights.append("🍛 Kamu sering belanja makan siang")
    insights.append("📆 Pengeluaran naik di akhir minggu")

    return {
        "insights": insights
    }
