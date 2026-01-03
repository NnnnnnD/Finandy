from app.core.database import SessionLocal
from app.models.users import User
from app.models.accounts import Account

db = SessionLocal()

# 1. create user
user = User(
    name="Nandy Naufal",
    email="naufalnandy11@gmail.com"
)
db.add(user)
db.commit()
db.refresh(user)

# 2. create accounts
bca = Account(
    user_id=user.id,
    name="myBCA",
    type="Balance"
)

cash = Account(
    user_id=user.id,
    name="Cash",
    type="Balance"
)

gopay = Account(
    user_id=user.id,
    name="GoPay",
    type="Balance"
)

blu = Account(
    user_id=user.id,
    name="bluBCA",
    type="Saving"
)

db.add_all([bca, cash, gopay, blu])
db.commit()

print("USER:", user.id)
print("BCA:", bca.id)
print("CASH:", cash.id)
print("GOPAY:", gopay.id)
print("BLU:", blu.id)
