from app.parsing.ml_fallback import ml_classify

def classify_transaction(text: str, *, user_accounts):
    text_l = text.lower()

    # ===== RULE BASED =====
    if any(k in text_l for k in ["transfer", "pindah", "top up", "topup", "tarik"]):
        return {"type": "transfer", "confidence": 0.9, "source": "rule"}

    if any(k in text_l for k in ["gaji", "bonus", "refund", "masuk"]):
        return {"type": "income", "confidence": 0.9, "source": "rule"}

    if any(k in text_l for k in ["beli", "bayar", "makan", "ngopi"]):
        return {"type": "expense", "confidence": 0.85, "source": "rule"}

    # ===== ML FALLBACK =====
    ml = ml_classify(text)
    if ml:
        return {
            "type": ml["label"],
            "confidence": ml["confidence"],
            "source": "ml",
        }

    # ===== DEFAULT =====
    return {"type": "expense", "confidence": 0.4, "source": "default"}
