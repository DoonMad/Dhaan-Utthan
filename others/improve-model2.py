import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split, RandomizedSearchCV
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, accuracy_score
from imblearn.over_sampling import SMOTE
from xgboost import XGBClassifier, plot_importance

# Load your dataset
data = pd.read_csv("./data/Crop_recommendation_real.csv")

# Handle missing values (replace with median)
data.fillna(data.median(), inplace=True)

# Separate features and target
X = data.drop(columns=["Best_Crop"])
y = data["Best_Crop"]

# Normalize numerical features
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Handle class imbalance using SMOTE
smote = SMOTE(random_state=42)
X_resampled, y_resampled = smote.fit_resample(X_scaled, y)

# Split data into train and test sets
X_train, X_test, y_train, y_test = train_test_split(X_resampled, y_resampled, test_size=0.2, random_state=42)

# Define hyperparameter search space
param_grid = {
    'n_estimators': [50, 100, 200],  # Reduce tree count
    'max_depth': [2, 3],  # Lower depth to prevent complex trees
    'learning_rate': [0.01, 0.05, 0.1],  # Keep learning rate low
    'gamma': [0.1, 0.2, 0.5],  # Increase to prevent unnecessary splits
    'subsample': [0.5, 0.7],  # Reduce to prevent overfitting
    'reg_lambda': [1, 5, 10],  # Increase L2 regularization
    'reg_alpha': [0.1, 0.5, 1],  # Increase L1 regularization
    'min_child_weight': [3, 5, 7]  # Increase to force splits on bigger patterns
}

# Initialize XGBoost classifier
xgb = XGBClassifier(eval_metric='logloss')

# Perform RandomizedSearch for best hyperparameters
random_search = RandomizedSearchCV(
    xgb, param_distributions=param_grid, n_iter=30, cv=5, n_jobs=-1, verbose=2
)
random_search.fit(X_train, y_train)

# Get best model
best_xgb = random_search.best_estimator_
print("Best Parameters:", random_search.best_params_)

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

# Test model on a new sample input
sample_input = np.array([[40, 30, 15, 6.5, 200, 30, 70]])  # Example values
sample_input = scaler.transform(sample_input)  # Apply same scaling as training
predicted_crop = best_xgb.predict(sample_input)
print("Predicted Crop (Encoded):", predicted_crop)
