from datetime import date
from sqlalchemy.orm import Session

from app.models.balance_checkpoints import BalanceCheckpoint
from app.ledger.calculator import calculate_balance_at


def ensure_daily_checkpoint(
    db: Session,
    *,
    account_id,
    target_date: date,
    source: str = "auto",
):
    """
    Ensure checkpoint exists for (account_id, target_date).
    Safe to call multiple times.
    """

    exists = (
        db.query(BalanceCheckpoint)
        .filter(
            BalanceCheckpoint.account_id == account_id,
            BalanceCheckpoint.checkpoint_date == target_date,
        )
        .first()
    )

    if exists:
        return exists

    balance = calculate_balance_at(db, account_id, target_date)

    cp = BalanceCheckpoint(
        account_id=account_id,
        checkpoint_date=target_date,
        balance=balance,
        source=source,
    )

    db.add(cp)
    db.commit()
    db.refresh(cp)

    return cp
