from app.nlp.ml_model import IntentModel

MODEL = IntentModel.load()

CONF_THRESHOLD = 0.75

def ml_classify(text: str):
    if not MODEL:
        return None

    res = MODEL.predict(text)

    if res["confidence"] < CONF_THRESHOLD:
        return None

    return res
