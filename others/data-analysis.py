import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder

# Load the dataset
data = pd.read_csv("../new_crop_data.csv")
data.rename(columns={"N": "Nitrogen", "P": "Phosphorus", "K": "Potassium", "ph": "pH_Level", "rainfall": "Rainfall", "temperature": "Temperature", "humidity": "Humidity", "label": "Best_Crop"}, inplace=True)

# Check class distribution
crop_counts = data["Best_Crop"].value_counts()
print("Crop Distribution:")
print(crop_counts)

# Plot class distribution
plt.figure(figsize=(10, 5))
plt.bar(crop_counts.index, crop_counts.values, color='skyblue')
plt.xlabel("Crop Type")
plt.ylabel("Count")
plt.title("Crop Distribution in Dataset")
plt.xticks(rotation=90)
plt.show()

# Check if dataset is imbalanced
max_count = crop_counts.max()
min_count = crop_counts.min()
imbalance_ratio = max_count / min_count

if imbalance_ratio > 2:
    print("Dataset is imbalanced.")
else:
    print("Dataset looks balanced.")

# Feature Correlation Analysis
plt.figure(figsize=(10, 8))
sns.heatmap(data.drop(columns=["Best_Crop"]).corr(), annot=True, cmap="coolwarm", fmt=".2f")
plt.title("Feature Correlation Matrix")
plt.show()

# Encode target labels
le = LabelEncoder()
data["Best_Crop"] = le.fit_transform(data["Best_Crop"])

# Define features and target
X = data.drop(columns=["Best_Crop"])
y = data["Best_Crop"]

# Train RandomForest model
rf = RandomForestClassifier(n_estimators=100, random_state=42)
rf.fit(X, y)

# Plot feature importance
feature_importances = pd.Series(rf.feature_importances_, index=X.columns)
feature_importances.sort_values(ascending=False).plot(kind='bar', color='lightcoral')
plt.xlabel("Features")
plt.ylabel("Importance")
plt.title("Feature Importance Analysis")
plt.show()
