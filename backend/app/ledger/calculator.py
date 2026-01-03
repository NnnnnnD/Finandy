from uuid import UUID
from datetime import date, datetime, time
from sqlalchemy.orm import Session

from app.models.transactions import Transaction
from app.models.balance_checkpoints import BalanceCheckpoint


def calculate_balance_at(db: Session, account_id, target_date: date):
    account_id = UUID(str(account_id))
    end_of_day = datetime.combine(target_date, time.max)

    checkpoint = (
        db.query(BalanceCheckpoint)
        .filter(
            BalanceCheckpoint.account_id == account_id,
            BalanceCheckpoint.checkpoint_date <= target_date,
        )
        .order_by(BalanceCheckpoint.checkpoint_date.desc())
        .first()
    )

    balance = checkpoint.balance if checkpoint else 0

    q = db.query(Transaction).filter(
        Transaction.transaction_at <= end_of_day
    )

    if checkpoint:
        start_dt = datetime.combine(checkpoint.checkpoint_date, time.min)
        q = q.filter(Transaction.transaction_at > start_dt)

    txs = q.filter(
        (Transaction.account_id == account_id)
        | (Transaction.to_account_id == account_id)
    ).order_by(Transaction.transaction_at.asc()).all()

    for tx in txs:
        if tx.type == "income" and tx.account_id == account_id:
            balance += tx.amount
        elif tx.type == "expense" and tx.account_id == account_id:
            balance -= tx.amount
        elif tx.type == "transfer":
            if tx.account_id == account_id:
                balance -= tx.amount
            elif tx.to_account_id == account_id:
                balance += tx.amount

    return balance
