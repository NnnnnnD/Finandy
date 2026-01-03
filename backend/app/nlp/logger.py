from sqlalchemy.orm import Session
from app.models.nlp_logs import NLPLog


def log_nlp(
    db: Session,
    *,
    user_id,
    raw_text: str,
    predicted: str,
    confidence: float,
    signals: dict | None = None,
):
    log = NLPLog(
        user_id=user_id,
        raw_text=raw_text,
        predicted_intent=predicted,
        confidence=confidence,
        signals=signals or {},
    )

    db.add(log)
    db.commit()
    db.refresh(log)

    return log
