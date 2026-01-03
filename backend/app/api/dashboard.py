from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.security import get_current_user

from app.db import get_db
from app.models import Account, BalanceCheckpoint

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/summary")
def dashboard_summary(user_id: str, db: Session = Depends(get_db)):
    accounts = (
        db.query(Account)
        .filter(Account.user_id == user_id)
        .all()
    )

    total_balance = 0
    result_accounts = []

    for acc in accounts:
        latest_checkpoint = (
            db.query(BalanceCheckpoint)
            .filter(BalanceCheckpoint.account_id == acc.id)
            .order_by(BalanceCheckpoint.checkpoint_date.desc())
            .first()
        )

        balance = latest_checkpoint.balance if latest_checkpoint else 0
        total_balance += balance

        result_accounts.append({
            "id": str(acc.id),
            "name": acc.name,
            "balance": balance,
            "is_primary": acc.is_primary,
        })

    return {
        "total_balance": total_balance,
        "accounts": result_accounts,
    }
