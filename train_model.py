import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import classification_report, accuracy_score
from imblearn.over_sampling import SMOTE
from xgboost import XGBClassifier, plot_importance
import os

# Load dataset
data = pd.read_csv("./data/Crop_recommendation_real.csv")

# Handle missing values (only for numeric columns)
numeric_cols = data.select_dtypes(include=[np.number]).columns
data[numeric_cols] = data[numeric_cols].fillna(data[numeric_cols].median())

# Encode categorical target variable
label_encoder = LabelEncoder()
data["label"] = label_encoder.fit_transform(data["label"])

# Separate features and target
X = data.drop(columns=["label"])
y = data["label"]

# Normalize numerical features
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Handle class imbalance using SMOTE
smote = SMOTE(random_state=42)
X_resampled, y_resampled = smote.fit_resample(X_scaled, y)

# Split data into train and test sets
X_train, X_test, y_train, y_test = train_test_split(X_resampled, y_resampled, test_size=0.2, random_state=42)

# Train best XGBoost model with optimized hyperparameters
best_xgb = XGBClassifier(n_estimators=100, max_depth=2, learning_rate=0.05, gamma=0.2, subsample=0.7, 
                         reg_lambda=5, reg_alpha=0.5, min_child_weight=3, eval_metric='logloss')

best_xgb.fit(X_train, y_train)

# Evaluate model
train_accuracy = best_xgb.score(X_train, y_train)
test_accuracy = best_xgb.score(X_test, y_test)

print(f"Training Accuracy: {train_accuracy:.4f}")
print(f"Test Accuracy: {test_accuracy:.4f}")

# Detailed classification report
y_pred = best_xgb.predict(X_test)
print("Classification Report:")
print(classification_report(y_test, y_pred))

# Feature importance visualization
plot_importance(best_xgb)
plt.title("Feature Importance in Crop Prediction Model")
plt.show()

# Save trained model and preprocessing tools
if not os.path.exists("pkl_files"):
    os.makedirs("pkl_files")
joblib.dump(best_xgb, "pkl_files/crop_prediction_xgb_model.pkl")
joblib.dump(label_encoder, "pkl_files/label_encoder.pkl")
joblib.dump(scaler, "pkl_files/scaler.pkl")

print("✅ Model training complete and saved successfully!")

# Test model on a new sample input
sample_input = np.array([[40, 30, 15, 6.5, 200, 30, 70]])  # Example values
sample_input = scaler.transform(sample_input)  # Apply same scaling as training
predicted_crop = best_xgb.predict(sample_input)
predicted_crop_label = label_encoder.inverse_transform(predicted_crop)
print("Predicted Crop:", predicted_crop_label[0])
