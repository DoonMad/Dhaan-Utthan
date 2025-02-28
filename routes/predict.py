from flask import Blueprint, request, jsonify
import pandas as pd
import joblib
import numpy as np
import os
import json
from datetime import datetime, timedelta
import openmeteo_requests
import requests_cache
from retry_requests import retry

predict_blueprint = Blueprint("predict", __name__)

# Get the absolute path of the current directory (routes)
current_dir = os.path.dirname(os.path.abspath(__file__))

# Construct correct paths
scaler_file_path = os.path.join(current_dir, "..", "models", "scaler.pkl")
label_encoder_file_path = os.path.join(current_dir, "..", "models", "label_encoder.pkl")
crop_model_file_path = os.path.join(current_dir, "..", "models", "crop_prediction_xgb_model.pkl")
crop_info_file_path = os.path.join(current_dir, "..", "data", "crop_info.json")
rainfall_file_path = os.path.join(current_dir, "..", "data", "rainfall.csv")

# Load Model and Preprocessing Files
model = joblib.load(crop_model_file_path)
label_encoder = joblib.load(label_encoder_file_path)
scaler = joblib.load(scaler_file_path)

# Load Crop Details
with open(crop_info_file_path, "r") as f:
    crop_info = json.load(f)

# Load Rainfall Dataset
rainfall_data = pd.read_csv(rainfall_file_path)

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
        return None, None

    year = datetime.now().year - 5  # Fetch data of 5 years before
    season_months = {"SUMMER": ("04-01", "06-30"), "MONSOON": ("07-01", "09-30"), "WINTER": ("12-01", "02-01")}
    start_date, end_date = season_months.get(season, ("01-01", "01-31"))
    start_date = f"{year}-{start_date}"
    # end_date = f"{year}-{end_date}"
    if(season == "WINTER"):
        end_date = f"{year + 1}-{end_date}"
    else:
        end_date = f"{year}-{end_date}"

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

    response = responses[0]
    hourly = response.Hourly()
    avg_temperature = np.mean(hourly.Variables(0).ValuesAsNumpy())
    avg_humidity = np.mean(hourly.Variables(1).ValuesAsNumpy())

    return avg_temperature, avg_humidity

# Get Rainfall Data from Dataset using Seasonal Columns
def get_rainfall(district, season):
    season_col_map = {"WINTER": "Oct-Dec", "SUMMER": "Mar-May", "MONSOON": "Jun-Sep"}
    row = rainfall_data[rainfall_data["DISTRICT"].str.strip().str.lower() == district.strip().lower()]
    if not row.empty and season in season_col_map:
        return row.iloc[0][season_col_map[season]]
    return 0  # Default to 0 if no data found

# Define feature names
feature_names = ["N", "P", "K", "temperature", "humidity", "ph", "rainfall"]

@predict_blueprint.route("/", methods=["POST"])
def predict_crop():
    try:
        # Get JSON input
        data = request.get_json()
        district = data.get("district", "").upper()
        nitrogen = data.get("N", 50.0)
        phosphorus = data.get("P", 30.0)
        potassium = data.get("K", 40.0)
        ph_level = data.get("ph", 6.5)
        if not district:
            return jsonify({"error": "District is required"}), 400

        predictions = {}

        for season in ["SUMMER", "MONSOON", "WINTER"]:
            # Fetch seasonal temperature, humidity, and rainfall
            temp, humidity = get_historical_weather(district, season)
            rainfall = get_rainfall(district, season)
            if temp is None:
                continue

            # Prepare input for model
            input_data = pd.DataFrame([[nitrogen, phosphorus, potassium, temp, humidity, ph_level, rainfall]],
                                      columns=feature_names)
            input_data_scaled = scaler.transform(input_data)

            # Make Prediction
            prediction_probs = model.predict_proba(input_data_scaled)[0]
            top_indices = np.argsort(prediction_probs)[-3:][::-1]
            top_crops = label_encoder.inverse_transform(top_indices)

            # Get Crop Details
            crop_details = [
                {
                    "name": crop.capitalize(),
                    "soil_type": crop_info.get(crop.capitalize(), {}).get("soil_type", "Unknown"),
                    "min_yield": crop_info.get(crop.capitalize(), {}).get("min_yield", 0),
                    "max_yield": crop_info.get(crop.capitalize(), {}).get("max_yield", 0),
                    "min_price": crop_info.get(crop.capitalize(), {}).get("min_price", 0),
                    "max_price": crop_info.get(crop.capitalize(), {}).get("max_price", 0),
                    "fertilizer": crop_info.get(crop.capitalize(), {}).get("fertilizer", "Unknown"),
                    "description": crop_info.get(crop.capitalize(), {}).get("description", "No description available"),
                    "confidence": f"{prediction_probs[idx] * 100:.2f}%"
                }
                for idx, crop in zip(top_indices, top_crops)
            ]

            predictions[season] = crop_details
        return jsonify(predictions), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
