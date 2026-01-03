from datetime import date
from sqlalchemy.orm import Session
from app.models.accounts import Account
from app.ledger.checkpoints import ensure_daily_checkpoint


def run_daily_checkpoints(db: Session, target_date: date):
    accounts = db.query(Account).all()

    for acc in accounts:
        ensure_daily_checkpoint(
            db,
            account_id=acc.id,
            target_date=target_date,
        )
