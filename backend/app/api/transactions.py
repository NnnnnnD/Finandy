from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from uuid import UUID

from app.db import get_db
from app.models import Transaction, Account  # ⬅️ IMPORT MODEL, BUKAN DEFINE

router = APIRouter(prefix="/transactions", tags=["Transactions"])


@router.get("/")
def list_transactions(
    user_id: UUID = Query(...),
    limit: int = Query(50),
    db: Session = Depends(get_db),
):
    transactions = (
        db.query(Transaction)
        .join(Account, Transaction.account_id == Account.id)
        .filter(Account.user_id == user_id)
        .order_by(Transaction.transaction_at.desc())
        .limit(limit)
        .all()
    )

    return [
        {
            "id": str(tx.id),
            "type": tx.type,
            "amount": tx.amount,
            "description": tx.description,
            "transaction_at": tx.transaction_at.isoformat(),
        }
        for tx in transactions
    ]
