"""
Generate a synthetic dataset for training a supervised learning model.
The model predicts how much a user is likely to spend on the website
based on their behavior and demographics.
"""

import pandas as pd
import numpy as np
import os

np.random.seed(42)

NUM_USERS = 1000

# Generate user features
data = {
    "user_id": range(1, NUM_USERS + 1),
    "age": np.random.randint(18, 70, NUM_USERS),
    "num_visits": np.random.randint(1, 100, NUM_USERS),
    "avg_session_duration_min": np.round(np.random.uniform(1, 60, NUM_USERS), 2),
    "num_items_viewed": np.random.randint(1, 200, NUM_USERS),
    "num_items_in_favorites": np.random.randint(0, 30, NUM_USERS),
    "num_previous_orders": np.random.randint(0, 50, NUM_USERS),
    "days_since_registration": np.random.randint(1, 730, NUM_USERS),
    "used_chat_assistant": np.random.choice([0, 1], NUM_USERS, p=[0.6, 0.4]),
    "is_returning_customer": np.random.choice([0, 1], NUM_USERS, p=[0.4, 0.6]),
}

df = pd.DataFrame(data)

# Generate target: total_spending (in USD)
# Based on a realistic formula with some noise
df["total_spending"] = (
    5.0 * df["num_previous_orders"]
    + 0.8 * df["num_visits"]
    + 0.5 * df["avg_session_duration_min"]
    + 0.3 * df["num_items_viewed"]
    + 2.0 * df["num_items_in_favorites"]
    + 15.0 * df["used_chat_assistant"]
    + 20.0 * df["is_returning_customer"]
    - 0.1 * df["age"]
    + 0.02 * df["days_since_registration"]
    + np.random.normal(0, 20, NUM_USERS)
)

# Ensure no negative spending
df["total_spending"] = np.maximum(df["total_spending"], 0)
df["total_spending"] = np.round(df["total_spending"], 2)

# Also generate a churn prediction target (will user leave in next 3 months?)
# Higher churn for users with low visits, low favorites, and old registration
churn_probability = (
    0.5
    - 0.005 * df["num_visits"]
    - 0.01 * df["num_items_in_favorites"]
    - 0.008 * df["num_previous_orders"]
    + 0.0003 * df["days_since_registration"]
    - 0.1 * df["used_chat_assistant"]
    + np.random.normal(0, 0.1, NUM_USERS)
)
churn_probability = np.clip(churn_probability, 0, 1)
df["will_churn"] = (churn_probability > 0.5).astype(int)

# Save dataset
output_dir = os.path.dirname(os.path.abspath(__file__))
output_path = os.path.join(output_dir, "user_behavior_dataset.csv")
df.to_csv(output_path, index=False)

print(f"Dataset generated with {NUM_USERS} users")
print(f"Saved to: {output_path}")
print(f"\nDataset shape: {df.shape}")
print(f"\nFeature statistics:")
print(df.describe())
print(f"\nChurn distribution:")
print(df["will_churn"].value_counts())
