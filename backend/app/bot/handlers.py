from datetime import date
from sqlalchemy.orm import Session

from app.models.accounts import Account
from app.models.transactions import Transaction
from app.models.nlp_logs import NLPLog

from app.bot.states import BotState
from app.bot.memory import get_state, set_state, clear_state

from app.parsing.parser import parse_transaction_text
from app.ledger.engine import apply_transaction
from app.ledger.calculator import calculate_balance_at
from app.ledger.checkpoints import ensure_daily_checkpoint

from app.bot.correction_utils import (
    resolve_time_window,
    parse_edit_instruction,
)

# =====================================================
# HELPERS
# =====================================================

def detect_account_in_text(text: str, accounts: list[Account]):
    text = text.lower().replace(" ", "")
    for acc in accounts:
        name = acc.name.lower().replace(" ", "")
        if name in text:
            return acc
    return None


def resolve_transfer_accounts(text: str, accounts: list[Account]):
    """
    Resolve transfer direction using natural language.
    Examples:
    - "dari BCA ke Mandiri"
    - "transfer ke gopay"
    """
    text_l = text.lower()
    from_acc = None
    to_acc = None

    for acc in accounts:
        if f"dari {acc.name.lower()}" in text_l:
            from_acc = acc
        if f"ke {acc.name.lower()}" in text_l:
            to_acc = acc

    if from_acc and to_acc:
        return from_acc, to_acc

    if to_acc:
        primary = next((a for a in accounts if a.is_primary), None)
        return primary, to_acc

    return None, None


# =====================================================
# MAIN HANDLER
# =====================================================

def handle_message(
    *,
    db: Session,
    telegram_user_id: str,
    user_id,
    text: str,
    user_accounts: list[Account],
):
    text_l = text.lower().strip()
    mem = get_state(telegram_user_id)

    # =====================================================
    # 🔎 CHECK BALANCE
    # =====================================================
    if text_l in ("cek saldo", "saldo", "check balance"):
        today = date.today()
        lines = []

        for acc in user_accounts:
            saldo = calculate_balance_at(db, acc.id, today)
            if saldo > 0:
                star = "⭐ " if acc.is_primary else ""
                lines.append(f"{star}{acc.name}: Rp {saldo:,}")

        if not lines:
            return {"reply": "💸 Semua akun kamu kosong."}

        return {"reply": "💰 Balance kamu sekarang:\n\n" + "\n".join(lines)}

    # =====================================================
    # 🛠 DETECT CORRECTION INTENT
    # =====================================================
    CORRECTION_KEYWORDS = [
        "salah", "bukan", "harusnya", "keliru", "revisi", "edit"
    ]

    if any(k in text_l for k in CORRECTION_KEYWORDS):
        set_state(
            telegram_user_id,
            BotState.CORRECT_SELECT_TX,
            {"raw_text": text},
        )
        return {
            "reply": (
                "Oke. Transaksi yang mana?\n"
                "Contoh:\n"
                "- kemarin siang\n"
                "- jam 7 malam\n"
                "- transaksi terakhir"
            )
        }

    # =====================================================
    # 🧭 CORRECTION: SELECT TRANSACTION
    # =====================================================
    if mem["state"] == BotState.CORRECT_SELECT_TX:
        start, end = resolve_time_window(text)

        txs = (
            db.query(Transaction)
            .filter(
                Transaction.transaction_at.between(start, end),
                Transaction.account.has(user_id=user_id),
            )
            .order_by(Transaction.transaction_at.desc())
            .limit(5)
            .all()
        )

        if not txs:
            clear_state(telegram_user_id)
            return {"reply": "❌ Gak nemu transaksi di waktu itu."}

        lines = []
        for i, tx in enumerate(txs, 1):
            lines.append(
                f"{i}. {tx.amount:,} ({tx.account.name}) "
                f"{tx.transaction_at.strftime('%d %b %H:%M')}"
            )

        set_state(
            telegram_user_id,
            BotState.CORRECT_APPLY_EDIT,
            {"candidates": [tx.id for tx in txs]},
        )

        return {
            "reply": (
                "Yang mana?\n" +
                "\n".join(lines) +
                "\n\nBalas dengan nomornya (1 / 2 / 3)"
            )
        }

    # =====================================================
    # ✏️ CORRECTION: APPLY EDIT
    # =====================================================
    if mem["state"] == BotState.CORRECT_APPLY_EDIT:
        pending = mem["pending"]

        # step 1: pilih nomor
        if "candidates" in pending and text_l.isdigit():
            idx = int(text_l) - 1
            ids = pending["candidates"]

            if idx < 0 or idx >= len(ids):
                return {"reply": "Nomor gak valid."}

            set_state(
                telegram_user_id,
                BotState.CORRECT_APPLY_EDIT,
                {"tx_id": ids[idx]},
            )

            return {
                "reply": (
                    "Oke. Mau diubah apa?\n"
                    "Contoh:\n"
                    "- harusnya 20rb\n"
                    "- bukan cash tapi BCA\n"
                    "- jam 11 siang"
                )
            }

        # step 2: apply edit
        if "tx_id" in pending:
            tx = db.query(Transaction).get(pending["tx_id"])
            updates = parse_edit_instruction(text, user_accounts)

            if not updates:
                return {"reply": "❌ Gak kebaca perubahannya."}

            if "amount" in updates:
                tx.amount = updates["amount"]

            if "account" in updates:
                tx.account_id = updates["account"].id

            if "transaction_at" in updates:
                tx.transaction_at = updates["transaction_at"]

            # 🔥 log correction ke NLP
            db.query(NLPLog).filter(
                NLPLog.raw_text == tx.description,
                NLPLog.user_id == user_id,
            ).update({
                "final_type": tx.type,
                "final_account": tx.account.name,
                "source": "corrected",
            })

            db.commit()
            clear_state(telegram_user_id)

            return {
                "reply": (
                    "✅ Transaksi berhasil diperbarui.\n"
                    f"- Jumlah: {tx.amount:,}\n"
                    f"- Akun: {tx.account.name}\n"
                    f"- Waktu: {tx.transaction_at.strftime('%d %b %H:%M')}"
                )
            }

    # =====================================================
    # ⏳ CONFIRM TRANSACTION
    # =====================================================
    if mem["state"] == BotState.AWAIT_CONFIRM:
        if text_l in ("ya", "y", "ok"):
            p = mem["pending"]

            ensure_daily_checkpoint(
                db,
                account_id=p["account_id"],
                target_date=p["transaction_at"].date(),
            )

            apply_transaction(db, **p)
            clear_state(telegram_user_id)
            return {"reply": "✅ Dicatat."}

        if text_l in ("tidak", "no", "gak", "cancel"):
            clear_state(telegram_user_id)
            return {"reply": "❌ Dibatalkan."}

        return {"reply": "Jawab **ya** atau **tidak** ya 🙂"}

    # =====================================================
    # 💸 NEW TRANSACTION
    # =====================================================
    try:
        parsed = parse_transaction_text(
            text,
            user_accounts=[a.name for a in user_accounts],
        )
    except ValueError:
        return {"reply": "❌ Nominal belum kebaca."}

    mentioned = detect_account_in_text(text, user_accounts)
    primary = next(a for a in user_accounts if a.is_primary)

    # ---------- TRANSFER ----------
    if parsed["type"] == "transfer":
        from_acc, to_acc = resolve_transfer_accounts(text, user_accounts)
        if not from_acc or not to_acc:
            return {"reply": "❌ Akun asal / tujuan belum jelas."}

        pending = {
            "account_id": from_acc.id,
            "to_account_id": to_acc.id,
            "tx_type": "transfer",
            "amount": parsed["amount"],
            "transaction_at": parsed["transaction_at"],
            "description": parsed["raw_text"],
        }

        set_state(telegram_user_id, BotState.AWAIT_CONFIRM, pending)
        return {
            "reply": (
                f"Konfirmasi ya:\n"
                f"- Tipe: transfer\n"
                f"- Jumlah: {parsed['amount']:,}\n"
                f"- Dari: {from_acc.name} → {to_acc.name}\n"
                f"- Waktu: {parsed['transaction_at']}\n\n"
                f"Ketik **ya** / **tidak**"
            )
        }

    # ---------- EXPENSE ----------
    from_acc = mentioned or primary

    pending = {
        "account_id": from_acc.id,
        "to_account_id": None,
        "tx_type": "expense",
        "amount": parsed["amount"],
        "transaction_at": parsed["transaction_at"],
        "description": parsed["raw_text"],
    }

    set_state(telegram_user_id, BotState.AWAIT_CONFIRM, pending)

    return {
        "reply": (
            f"Konfirmasi ya:\n"
            f"- Tipe: expense\n"
            f"- Jumlah: {parsed['amount']:,}\n"
            f"- Dari: {from_acc.name}\n"
            f"- Waktu: {parsed['transaction_at']}\n\n"
            f"Ketik **ya** / **tidak**"
        )
    }
