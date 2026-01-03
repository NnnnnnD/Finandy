from app.core.database import SessionLocal
from app.models.nlp_logs import NLPLog
from app.nlp.ml_model import IntentModel

def train_model():
    db = SessionLocal()

    rows = db.query(NLPLog).filter(
        NLPLog.final_type.isnot(None)
    ).all()

    texts = [r.raw_text for r in rows]
    labels = [r.final_type for r in rows]

    model = IntentModel()
    model.train(texts, labels)
    model.save()

    print(f"✅ Model trained with {len(rows)} samples")

if __name__ == "__main__":
    train_model()
