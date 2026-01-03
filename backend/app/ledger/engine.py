from sqlalchemy.orm import Session
from app.models.transactions import Transaction


def apply_transaction(
    db: Session,
    *,
    account_id,
    tx_type: str,
    amount: int,
    transaction_at,
    description: str = None,
    to_account_id=None,
):
    if tx_type == "transfer" and not to_account_id:
        raise ValueError("Transfer requires to_account_id")

    tx = Transaction(
        account_id=account_id,
        to_account_id=to_account_id,
        type=tx_type,
        amount=amount,
        transaction_at=transaction_at,
        description=description,
    )

    db.add(tx)
    db.commit()
    db.refresh(tx)
    return tx
