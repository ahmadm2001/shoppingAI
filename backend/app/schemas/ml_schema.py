from pydantic import BaseModel
from typing import Optional


class PredictionRequest(BaseModel):
    age: int = 30
    num_visits: int = 10
    avg_session_duration_min: float = 15.0
    num_items_viewed: int = 20
    num_items_in_favorites: int = 5
    num_previous_orders: int = 3
    days_since_registration: int = 90
    used_chat_assistant: int = 0  # 0 or 1
    is_returning_customer: int = 1  # 0 or 1


class SpendingPredictionResponse(BaseModel):
    predicted_spending: float
    confidence: str


class ChurnPredictionResponse(BaseModel):
    will_churn: bool
    churn_probability: float
    risk_level: str
