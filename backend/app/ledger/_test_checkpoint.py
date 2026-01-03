from datetime import date
from app.core.database import SessionLocal
from app.ledger.checkpoints import create_checkpoint
from app.ledger.calculator import calculate_balance_at

db = SessionLocal()

BCA_ID = "7c81e30c-ef53-4fdc-873e-1f379a98d9c1"

create_checkpoint(
    db,
    account_id=BCA_ID,
    balance=5_000_000,
    checkpoint_date=date(2025, 12, 15),
)

print(calculate_balance_at(db, BCA_ID, date(2025, 12, 30)))
