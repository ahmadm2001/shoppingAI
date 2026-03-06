from fastapi import APIRouter

from app.schemas.ml_schema import (
    PredictionRequest,
    SpendingPredictionResponse,
    ChurnPredictionResponse,
)
from app.services.ml_service import predict_spending, predict_churn

router = APIRouter(prefix="/ml", tags=["Machine Learning Predictions"])


@router.post("/predict-spending", response_model=SpendingPredictionResponse)
def predict_user_spending(request: PredictionRequest):
    """Predict how much a user is likely to spend based on their behavior."""
    features = request.model_dump()
    return predict_spending(features)


@router.post("/predict-churn", response_model=ChurnPredictionResponse)
def predict_user_churn(request: PredictionRequest):
    """Predict whether a user is likely to leave the website."""
    features = request.model_dump()
    return predict_churn(features)
