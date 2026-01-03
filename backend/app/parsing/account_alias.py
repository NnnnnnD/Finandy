import re
import difflib
from typing import Optional
from sqlalchemy.orm import Session

from app.models.accounts import Account
from app.models.account_aliases import AccountAlias


def normalize(text: str) -> str:
    return re.sub(r"[^a-z0-9]", "", text.lower())


def resolve_account(
    db: Session,
    *,
    text: str,
    user_accounts: list[Account],
    learn: bool = True,
) -> Optional[Account]:
    """
    Resolve account from free text using:
    1. exact alias
    2. fuzzy alias
    3. direct account name
    """

    tokens = normalize(text)

    # === 1️⃣ exact alias ===
    aliases = (
        db.query(AccountAlias)
        .join(Account, Account.id == AccountAlias.account_id)
        .filter(Account.user_id == user_accounts[0].user_id)
        .all()
    )

    for a in aliases:
        if a.alias in tokens:
            return next(acc for acc in user_accounts if acc.id == a.account_id)

    # === 2️⃣ fuzzy alias ===
    alias_map = {a.alias: a.account_id for a in aliases}
    matches = difflib.get_close_matches(tokens, alias_map.keys(), cutoff=0.75)

    if matches:
        acc_id = alias_map[matches[0]]
        acc = next(acc for acc in user_accounts if acc.id == acc_id)

        if learn:
            db.add(AccountAlias(
                account_id=acc.id,
                alias=tokens,
            ))
            db.commit()

        return acc

    # === 3️⃣ direct account name ===
    for acc in user_accounts:
        if normalize(acc.name) in tokens:
            return acc

    return None
