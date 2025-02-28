from flask import Blueprint, request, jsonify
import pandas as pd
import os
import pandas as pd

# Get the absolute path of the current directory (routes)
current_dir = os.path.dirname(os.path.abspath(__file__))

# Construct the correct path to rainfall.csv
rainfall_file_path = os.path.join(current_dir, "..", "data", "rainfall.csv")

# Load the Rainfall Dataset
rainfall_data = pd.read_csv(rainfall_file_path)

rainfall_blueprint = Blueprint("rainfall", __name__)
# Get Rainfall Data from Dataset using Seasonal Columns
def get_rainfall(district, season):
    season_col_map = {"WINTER": "Oct-Dec", "SUMMER": "Mar-May", "MONSOON": "Jun-Sep"}
    
    # Convert input to lowercase for case-insensitive match
    row = rainfall_data[rainfall_data["DISTRICT"].str.strip().str.lower() == district.strip().lower()]
    
    if not row.empty and season in season_col_map:
        return row.iloc[0][season_col_map[season]]
    
    return None  # Return None if no data is found

# Define Rainfall API Route
@rainfall_blueprint.route("/", methods=["GET"])
def fetch_rainfall():
    try:
        district = request.args.get("district")
        if not district:
            return jsonify({"error": "District is required"}), 400

        rainfall_data_response = {}
        for season in ["SUMMER", "MONSOON", "WINTER"]:
            rainfall = get_rainfall(district, season)
            if rainfall is not None:
                rainfall_data_response[season] = f"{rainfall} mm"
            else:
                rainfall_data_response[season] = {"error": "No rainfall data found"}

        return jsonify(rainfall_data_response), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
