from datetime import date
from app.core.database import SessionLocal
from app.ledger.engine import apply_transaction
from app.ledger.calculator import calculate_balance_at

db = SessionLocal()

# ganti dengan UUID account lo
BCA_ID = "7c81e30c-ef53-4fdc-873e-1f379a98d9c1"

apply_transaction(
    db,
    account_id=BCA_ID,
    tx_type="income",
    amount=1_000_000,
    tx_date=date.today(),
    description="Gaji",
)

apply_transaction(
    db,
    account_id=BCA_ID,
    tx_type="expense",
    amount=200_000,
    tx_date=date.today(),
    description="Makan",
)

balance = calculate_balance_at(db, BCA_ID, date.today())
print("Balance:", balance)
