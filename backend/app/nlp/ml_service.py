from app.nlp.ml_model import TransactionIntentModel

_model = TransactionIntentModel()
_model.load()


def ml_predict_intent(text: str):
    if not _model.model:
        return None, 0.0

    return _model.predict(text)
