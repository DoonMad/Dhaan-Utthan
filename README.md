# 🌾 Dhaan-Utthan - Smart Crop Prediction System

Dhaan-Utthan is an AI-powered crop prediction tool designed to help farmers make informed decisions about which crops to plant based on weather conditions, soil nutrients, and historical climate data.

## 🚀 Features

- **Weather Integration:** Fetches historical temperature, humidity, and rainfall data.
- **Soil Analysis:** Uses nitrogen, phosphorus, potassium, and pH level inputs.
- **AI-Based Crop Prediction:** Uses an XGBoost model to predict the best crops for each season.
- **Seasonal Insights:** Provides crop recommendations for Summer, Monsoon, and Winter.
- **Detailed Crop Information:** Displays soil type, expected yield, market price, and fertilizers.

## 🛠 Tech Stack

### Frontend:
- **React.js** - For building a responsive and dynamic UI.
- **CSS** - For styling and layout.

### Backend:
- **Flask** - Lightweight Python web framework for API development.
- **Open-Meteo API** - To fetch historical weather data.
- **Pandas & NumPy** - For data processing.

### Machine Learning:
- **XGBoost** - Gradient boosting algorithm used for crop prediction.
- **Scikit-Learn** - Used for preprocessing, scaling, and encoding.

## 📊 How It Works

1. **User Inputs District & Soil Data**
   - The user enters nitrogen, phosphorus, potassium, and pH levels.
   - Selects the district for weather-based predictions.

2. **Weather Data Retrieval**
   - Historical temperature and humidity are fetched using Open-Meteo API.
   - Rainfall data is taken from an existing dataset.

3. **Crop Prediction Using ML**
   - The input data is scaled and processed.
   - XGBoost predicts the best crops for the selected district and season.
   - The system ranks crops based on suitability.

4. **Results Displayed in an Interactive UI**
   - Recommended crops are shown in a visually appealing way with images and details.
   - Farmers get guidance on soil type, yield, price range, and fertilizer requirements.

## 📦 Installation

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/your-repo/dhaan-utthan.git
cd dhaan-utthan
```
### 2️⃣ Backend Setup
```bash
pip install -r requirements.txt
python app.py
```
The backend will start on http://127.0.0.1:5001/
### 3️⃣ Frontend Setup
```bash
cd frontend
npm install
npm start
```
The frontend will run on http://localhost:3000/

## 🎯 Future Enhancements
- Profit Prediction based on market prices and expected yield.
- Multi-Language Support for better accessibility.
- Database Integration for saving user data and analysis.
- Mobile App Version to improve accessibility for farmers.

## 🤝 Contributing
Feel free to fork this repository and contribute!
