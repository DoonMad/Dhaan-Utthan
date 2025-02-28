import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import seaborn as sns
import matplotlib.pyplot as plt

# Load dataset
data = pd.read_csv("./data/Crop_recommendation_real.csv")
data.rename(columns={"N": "Nitrogen", "P": "Phosphorus", "K": "Potassium", "ph": "pH_Level", "rainfall": "Rainfall", "temperature": "Temperature", "humidity": "Humidity", "label": "Best_Crop"}, inplace=True)

# Encode target variable
data["Best_Crop"] = data["Best_Crop"].astype('category').cat.codes

# Define features and target
X = data.drop(columns=["Best_Crop"])
y = data["Best_Crop"]

# Split data into train and test sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Load trained model
model = joblib.load("crop_prediction_xgb_model.pkl")

# Evaluate on training data
y_train_pred = model.predict(X_train)
train_accuracy = accuracy_score(y_train, y_train_pred)
print(f"Training Accuracy: {train_accuracy:.4f}")

# Evaluate on test data
y_test_pred = model.predict(X_test)
test_accuracy = accuracy_score(y_test, y_test_pred)
print(f"Test Accuracy: {test_accuracy:.4f}")

# Classification report
print("Classification Report for Test Data:")
print(classification_report(y_test, y_test_pred))

# Confusion Matrix
plt.figure(figsize=(10, 6))
sns.heatmap(confusion_matrix(y_test, y_test_pred), annot=True, fmt="d", cmap="Blues")
plt.xlabel("Predicted")
plt.ylabel("Actual")
plt.title("Confusion Matrix")
plt.show()
