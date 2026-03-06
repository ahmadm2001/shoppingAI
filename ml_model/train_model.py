"""
Train supervised learning models:
1. Regression model: Predict user spending
2. Classification model: Predict user churn

Uses scikit-learn with RandomForest for both tasks.
"""

import pandas as pd
import numpy as np
import pickle
import os
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score,
    accuracy_score,
    classification_report,
    confusion_matrix,
)
from sklearn.preprocessing import StandardScaler

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_PATH = os.path.join(BASE_DIR, "user_behavior_dataset.csv")
SPENDING_MODEL_PATH = os.path.join(BASE_DIR, "spending_model.pkl")
CHURN_MODEL_PATH = os.path.join(BASE_DIR, "churn_model.pkl")
SCALER_PATH = os.path.join(BASE_DIR, "scaler.pkl")


def load_data():
    """Load and prepare the dataset."""
    df = pd.read_csv(DATASET_PATH)
    print(f"Loaded dataset with {len(df)} records")
    return df


def train_spending_model(df):
    """Train a regression model to predict user spending."""
    print("\n" + "=" * 60)
    print("TRAINING SPENDING PREDICTION MODEL")
    print("=" * 60)

    features = [
        "age", "num_visits", "avg_session_duration_min",
        "num_items_viewed", "num_items_in_favorites",
        "num_previous_orders", "days_since_registration",
        "used_chat_assistant", "is_returning_customer",
    ]

    X = df[features]
    y = df["total_spending"]

    # Scale features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X_scaled, y, test_size=0.2, random_state=42
    )

    # Train model
    model = RandomForestRegressor(
        n_estimators=100,
        max_depth=10,
        random_state=42,
        n_jobs=-1,
    )
    model.fit(X_train, y_train)

    # Evaluate
    y_pred = model.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    r2 = r2_score(y_test, y_pred)

    print(f"\nSpending Model Results:")
    print(f"  MAE:  ${mae:.2f}")
    print(f"  RMSE: ${rmse:.2f}")
    print(f"  R²:   {r2:.4f}")

    # Feature importance
    importance = pd.DataFrame({
        "feature": features,
        "importance": model.feature_importances_,
    }).sort_values("importance", ascending=False)
    print(f"\nFeature Importance:")
    for _, row in importance.iterrows():
        print(f"  {row['feature']}: {row['importance']:.4f}")

    # Save model and scaler
    with open(SPENDING_MODEL_PATH, "wb") as f:
        pickle.dump(model, f)
    with open(SCALER_PATH, "wb") as f:
        pickle.dump(scaler, f)

    print(f"\nModel saved to: {SPENDING_MODEL_PATH}")
    return model, scaler


def train_churn_model(df):
    """Train a classification model to predict user churn."""
    print("\n" + "=" * 60)
    print("TRAINING CHURN PREDICTION MODEL")
    print("=" * 60)

    features = [
        "age", "num_visits", "avg_session_duration_min",
        "num_items_viewed", "num_items_in_favorites",
        "num_previous_orders", "days_since_registration",
        "used_chat_assistant", "is_returning_customer",
    ]

    X = df[features]
    y = df["will_churn"]

    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # Train model
    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        random_state=42,
        n_jobs=-1,
    )
    model.fit(X_train, y_train)

    # Evaluate
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)

    print(f"\nChurn Model Results:")
    print(f"  Accuracy: {accuracy:.4f}")
    print(f"\nClassification Report:")
    print(classification_report(y_test, y_pred))
    print(f"Confusion Matrix:")
    print(confusion_matrix(y_test, y_pred))

    # Save model
    with open(CHURN_MODEL_PATH, "wb") as f:
        pickle.dump(model, f)

    print(f"\nModel saved to: {CHURN_MODEL_PATH}")
    return model


if __name__ == "__main__":
    # First generate dataset if it doesn't exist
    if not os.path.exists(DATASET_PATH):
        print("Generating dataset...")
        exec(open(os.path.join(BASE_DIR, "generate_dataset.py")).read())

    df = load_data()
    spending_model, scaler = train_spending_model(df)
    churn_model = train_churn_model(df)

    print("\n" + "=" * 60)
    print("ALL MODELS TRAINED SUCCESSFULLY")
    print("=" * 60)
