import pickle
import os
import numpy as np

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ML_DIR = os.path.join(BASE_DIR, "ml_models")

SPENDING_MODEL_PATH = os.path.join(ML_DIR, "spending_model.pkl")
CHURN_MODEL_PATH = os.path.join(ML_DIR, "churn_model.pkl")
SCALER_PATH = os.path.join(ML_DIR, "scaler.pkl")

_spending_model = None
_churn_model = None
_scaler = None


def _load_models():
    """Load ML models from disk."""
    global _spending_model, _churn_model, _scaler

    if _spending_model is None and os.path.exists(SPENDING_MODEL_PATH):
        with open(SPENDING_MODEL_PATH, "rb") as f:
            _spending_model = pickle.load(f)

    if _churn_model is None and os.path.exists(CHURN_MODEL_PATH):
        with open(CHURN_MODEL_PATH, "rb") as f:
            _churn_model = pickle.load(f)

    if _scaler is None and os.path.exists(SCALER_PATH):
        with open(SCALER_PATH, "rb") as f:
            _scaler = pickle.load(f)


def predict_spending(features: dict) -> dict:
    """Predict how much a user will spend."""
    _load_models()

    if _spending_model is None or _scaler is None:
        return {
            "predicted_spending": 0.0,
            "confidence": "Model not available",
        }

    feature_array = np.array([[
        features["age"],
        features["num_visits"],
        features["avg_session_duration_min"],
        features["num_items_viewed"],
        features["num_items_in_favorites"],
        features["num_previous_orders"],
        features["days_since_registration"],
        features["used_chat_assistant"],
        features["is_returning_customer"],
    ]])

    scaled = _scaler.transform(feature_array)
    prediction = _spending_model.predict(scaled)[0]

    return {
        "predicted_spending": round(max(prediction, 0), 2),
        "confidence": "high" if features["num_visits"] > 10 else "medium",
    }


def predict_churn(features: dict) -> dict:
    """Predict whether a user will churn."""
    _load_models()

    if _churn_model is None:
        return {
            "will_churn": False,
            "churn_probability": 0.0,
            "risk_level": "Model not available",
        }

    feature_array = np.array([[
        features["age"],
        features["num_visits"],
        features["avg_session_duration_min"],
        features["num_items_viewed"],
        features["num_items_in_favorites"],
        features["num_previous_orders"],
        features["days_since_registration"],
        features["used_chat_assistant"],
        features["is_returning_customer"],
    ]])

    prediction = _churn_model.predict(feature_array)[0]
    probability = _churn_model.predict_proba(feature_array)[0][1]

    risk_level = "low"
    if probability > 0.7:
        risk_level = "high"
    elif probability > 0.4:
        risk_level = "medium"

    return {
        "will_churn": bool(prediction),
        "churn_probability": round(float(probability), 4),
        "risk_level": risk_level,
    }
