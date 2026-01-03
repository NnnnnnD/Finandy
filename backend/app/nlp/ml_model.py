import joblib
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

MODEL_PATH = Path("models/intent_model.joblib")

class IntentModel:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(ngram_range=(1, 2))
        self.model = LogisticRegression(max_iter=1000)

    def train(self, texts, labels):
        X = self.vectorizer.fit_transform(texts)
        self.model.fit(X, labels)

    def predict(self, text):
        X = self.vectorizer.transform([text])
        proba = self.model.predict_proba(X)[0]
        idx = proba.argmax()
        return {
            "label": self.model.classes_[idx],
            "confidence": float(proba[idx]),
        }

    def save(self):
        joblib.dump(self, MODEL_PATH)

    @staticmethod
    def load():
        if not MODEL_PATH.exists():
            return None
        return joblib.load(MODEL_PATH)
