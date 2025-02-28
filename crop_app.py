import streamlit as st
import pandas as pd
import joblib
import numpy as np
import matplotlib.pyplot as plt
import requests
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
import openmeteo_requests
import requests_cache
from retry_requests import retry

# Load environment variables
load_dotenv()

# Load trained model and preprocessing files
model = joblib.load("./pkl_files/crop_prediction_xgb_model.pkl")
label_encoder = joblib.load("./pkl_files/label_encoder.pkl")
scaler = joblib.load("./pkl_files/scaler.pkl")

# Define feature names
feature_names = ["N", "P", "K", "temperature", "humidity", "ph", "rainfall"]

# Define crop seasons
season_crops = {
    "SUMMER": ["Maize", "Mango", "Watermelon", "Muskmelon", "Pomegranate"],
    "MONSOON": ["Rice", "Pigeonpeas", "Blackgram", "Orange", "Jute", "Cotton"],
    "WINTER": ["Wheat", "Chickpea", "Lentil", "Kidneybeans", "Apple", "Grapes", "Papaya"]
}

# Load Rainfall Dataset
rainfall_data = pd.read_csv("./data/rainfall.csv")  # Ensure this file exists

# Open-Meteo API Configuration
cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
openmeteo = openmeteo_requests.Client(session=retry_session)

# Function to get latitude and longitude for a district
def get_lat_lon(district):
    row = rainfall_data[rainfall_data["DISTRICT"].str.strip().str.lower() == district.strip().lower()]
    if not row.empty:
        coord_str = row.iloc[0]["coord"]
        coord_dict = eval(coord_str.strip())  # Convert string to dictionary
        return coord_dict["lat"], coord_dict["lon"]
    return None, None

# Function to fetch historical temperature and humidity using Open-Meteo API
def get_historical_weather(district, season):
    lat, lon = get_lat_lon(district)
    if lat is None or lon is None:
        st.warning(f"⚠️ Could not fetch coordinates for {district}.")
        return None, None

    # Define date ranges for each season
    year = datetime.now().year - 5  # Fetch data of 5 yr before
    if season == "SUMMER":
        start_date = f"{year}-04-01"
        end_date = f"{year}-06-30"
    elif season == "MONSOON":
        start_date = f"{year}-07-01"
        end_date = f"{year}-09-30"
    elif season == "WINTER":
        start_date = f"{year}-12-01"
        end_date = f"{year + 1}-02-28"
    else:
        st.warning(f"⚠️ Invalid season: {season}.")
        return None, None

    # Make API request
    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": start_date,
        "end_date": end_date,
        "hourly": ["temperature_2m", "relative_humidity_2m"],
        "timezone": "Asia/Kolkata"
    }
    responses = openmeteo.weather_api(url, params=params)

    # Process the response
    response = responses[0]
    hourly = response.Hourly()
    hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()
    hourly_relative_humidity_2m = hourly.Variables(1).ValuesAsNumpy()

    # Calculate average temperature and humidity
    avg_temperature = np.mean(hourly_temperature_2m)
    avg_humidity = np.mean(hourly_relative_humidity_2m)

    return avg_temperature, avg_humidity

# Get Rainfall Data from Dataset using Seasonal Columns
def get_rainfall(district, season):
    season_col_map = {"WINTER": "Oct-Dec", "SUMMER": "Mar-May", "MONSOON": "Jun-Sep"}
    row = rainfall_data[rainfall_data["DISTRICT"] == district]
    if not row.empty and season in season_col_map:
        return row.iloc[0][season_col_map[season]]
    return 0  # Default to 0 if no data found

# Streamlit App UI
st.title("🌾 Crop Prediction Web App")
st.write("Enter soil and climate conditions to find the best crop to plant.")

# Select District (User Input)
selected_district = st.text_input("Enter District (Only Indian Cities)", "Mumbai")
selected_district = selected_district.upper()

# User input fields
nitrogen = st.number_input("N", min_value=0.0, value=50.0)
phosphorus = st.number_input("P", min_value=0.0, value=30.0)
potassium = st.number_input("K", min_value=0.0, value=40.0)
pH_level = st.number_input("ph", min_value=0.0, max_value=14.0, value=6.5)

# Fetch Weather Data Button
if st.button("Fetch Weather Data"):
    st.write("## 🌦 Weather Data for Each Season")
    for season in ["SUMMER", "MONSOON", "WINTER"]:
        temperature, humidity = get_historical_weather(selected_district, season)
        rainfall = get_rainfall(selected_district, season)
        if temperature is not None:
            st.write(f"### {season}")
            st.success(f"🌡 Average Temperature: {temperature:.2f}°C, 💧 Average Humidity: {humidity:.2f}%, 🌧 Rainfall: {rainfall} mm")
        else:
            st.warning(f"⚠️ Could not fetch weather data for {selected_district} in {season}.")

# Predict Crop Button
if st.button("Predict Crop"):
    st.write("## 🌍 Best Crops for Each Season")
    crop_recommendations = {}
    for season, crops in season_crops.items():
        season_predictions = []
        temperature, humidity = get_historical_weather(selected_district, season)
        rainfall = get_rainfall(selected_district, season)
        if temperature is not None:
            input_data = pd.DataFrame([[nitrogen, phosphorus, potassium, temperature, humidity, pH_level, rainfall]],
                                      columns=feature_names)
            input_data_scaled = scaler.transform(input_data)
            prediction_probs = model.predict_proba(input_data_scaled)[0]
            top_indices = np.argsort(prediction_probs)[-3:][::-1]
            top_crops = label_encoder.inverse_transform(top_indices)
            season_predictions.extend(top_crops)
        crop_recommendations[season] = list(set(season_predictions))

    for season, crops in crop_recommendations.items():
        st.write(f"### 🌿 {season} Season")
        if crops:
            st.write(", ".join(crops))
        else:
            st.write("No suitable crops found for this season based on input conditions.")