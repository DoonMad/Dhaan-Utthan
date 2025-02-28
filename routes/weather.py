from flask import Blueprint, request, jsonify
import pandas as pd
import numpy as np
from datetime import datetime
import requests

weather_blueprint = Blueprint('weather', __name__)

# Load Rainfall Dataset
rainfall_data = pd.read_csv("./data/rainfall.csv")

# Open-Meteo API Configuration
METEO_API_URL = "https://archive-api.open-meteo.com/v1/archive"

def get_lat_lon(district):
    """Fetch latitude and longitude from the rainfall dataset."""
    row = rainfall_data[rainfall_data["DISTRICT"].str.strip().str.lower() == district.strip().lower()]
    if not row.empty:
        coord_str = row.iloc[0]["coord"]
        coord_dict = eval(coord_str.strip())  # Convert string to dictionary
        return coord_dict["lat"], coord_dict["lon"]
    return None, None

def get_historical_weather(district, season):
    """Fetch historical temperature and humidity from Open-Meteo API."""
    lat, lon = get_lat_lon(district)
    if lat is None or lon is None:
        return None, None

    # Define date ranges for each season (fetching 5-year-old data for consistency)
    year = datetime.now().year - 5  
    season_dates = {
        "SUMMER": (f"{year}-04-01", f"{year}-06-30"),
        "MONSOON": (f"{year}-07-01", f"{year}-09-30"),
        "WINTER": (f"{year}-12-01", f"{year+1}-02-28")
    }
    
    if season not in season_dates:
        return None, None  # Invalid season

    start_date, end_date = season_dates[season]

    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": start_date,
        "end_date": end_date,
        "hourly": ["temperature_2m", "relative_humidity_2m"],
        "timezone": "Asia/Kolkata"
    }
    
    response = requests.get(METEO_API_URL, params=params)
    
    if response.status_code == 200 and "hourly" in response.json():
        data = response.json()["hourly"]
        avg_temp = np.mean(data["temperature_2m"])
        avg_humidity = np.mean(data["relative_humidity_2m"])
        return avg_temp, avg_humidity

    return None, None

def get_rainfall(district, season):
    """Fetch seasonal rainfall for a given district from the dataset."""
    season_col_map = {"WINTER": "Oct-Dec", "SUMMER": "Mar-May", "MONSOON": "Jun-Sep"}

    # Normalize district name (remove spaces, make lowercase)
    district = district.strip().lower()

    # Find matching district in the dataset
    row = rainfall_data[rainfall_data["DISTRICT"].str.strip().str.lower() == district]

    if not row.empty and season in season_col_map:
        return row.iloc[0][season_col_map[season]]  # Get rainfall for the season

    return 0  # Default to 0 if no data found

@weather_blueprint.route('/', methods=['GET'])
def get_weather():
    """API route to fetch weather data (temperature, humidity, rainfall)."""
    district = request.args.get('district')

    if not district:
        return jsonify({"error": "District parameter is required"}), 400

    seasonal_weather = {}

    for season in ["SUMMER", "MONSOON", "WINTER"]:
        temperature, humidity = get_historical_weather(district, season)
        rainfall = get_rainfall(district, season)  # Fetch rainfall from dataset

        if temperature is None:
            return jsonify({"error": f"Could not fetch data for {district} in {season}"}), 500

        seasonal_weather[season] = {
            "temperature": f"{temperature:.2f}°C",
            "humidity": f"{humidity:.2f}%",
            "rainfall": f"{rainfall} mm"  # Include rainfall data
        }

    return jsonify(seasonal_weather)
