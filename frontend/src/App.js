import React, { useState } from "react";
import axios from "axios";

const App = () => {
  const [district, setDistrict] = useState("Mumbai");
  const [weatherData, setWeatherData] = useState(null);
  const [cropPredictions, setCropPredictions] = useState(null);
  const [inputs, setInputs] = useState({
    N: 50,
    P: 30,
    K: 40,
    ph: 6.5
  });

  const handleChange = (e) => {
    setInputs({ ...inputs, [e.target.name]: parseFloat(e.target.value) });
  };

  // Fetch Weather Data including Rainfall
  const fetchWeather = async () => {
    try {
      const response = await axios.get(`http://127.0.0.1:5001/weather/?district=${district}`);
      setWeatherData(response.data);
    } catch (error) {
      console.error("Error fetching weather data:", error);
    }
  };

  // Predict Crops based on Weather & Soil Inputs
  const predictCrops = async () => {
    try {
      const response = await axios.post("http://127.0.0.1:5001/predict/", {
        district,
        ...inputs
      });
      setCropPredictions(response.data);
    } catch (error) {
      console.error("Error predicting crops:", error);
    }
  };

  return (
    <div>
      <h1>🌾 Crop Prediction App</h1>

      {/* User Input for District */}
      <label>Enter District: </label>
      <input type="text" value={district} onChange={(e) => setDistrict(e.target.value)} />

      {/* Input Fields for Soil & Climate Conditions */}
      <h3>Enter Soil and Climate Conditions:</h3>
      <label>Nitrogen (mg/kg): </label>
      <input type="number" name="N" value={inputs.N} onChange={handleChange} />

      <label>Phosphorus (mg/kg): </label>
      <input type="number" name="P" value={inputs.P} onChange={handleChange} />

      <label>Potassium (mg/kg): </label>
      <input type="number" name="K" value={inputs.K} onChange={handleChange} />

      <label>pH Level: </label>
      <input type="number" name="ph" value={inputs.ph} onChange={handleChange} />

      {/* Action Buttons */}
      <button onClick={fetchWeather}>Get Weather Data</button>
      <button onClick={predictCrops}>Predict Crops</button>

      {/* Weather Data Display */}
      {weatherData && (
        <div>
          <h2>🌦 Seasonal Weather Data</h2>
          {Object.entries(weatherData).map(([season, values]) => (
            <div key={season}>
              <h3>📅 {season}</h3>
              <p>🌡 Temperature: {values.temperature}</p>
              <p>💧 Humidity: {values.humidity}</p>
              <p>🌧 Rainfall: {values.rainfall} mm</p> {/* ✅ Rainfall Data Included */}
            </div>
          ))}
        </div>
      )}

      {/* Crop Prediction Display */}
      {cropPredictions && (
        <div>
          <h2>🌱 Recommended Crops</h2>
          {Object.entries(cropPredictions).map(([season, crops]) => (
            <div key={season}>
              <h3>📅 {season} Season</h3>
              {crops.length > 0 ? (
                crops.map((crop, index) => (
                  <div key={index}>
                    <h4>🌾 {crop.name}</h4>
                    <p><strong>Soil Type:</strong> {crop.soil_type}</p>
                    <p><strong>Yield:</strong> {crop.min_yield} - {crop.max_yield} tons</p>
                    <p><strong>Price:</strong> ₹{crop.min_price} - ₹{crop.max_price} per kg</p>
                    <p><strong>Recommended Fertilizer:</strong> {crop.fertilizer}</p>
                    <p>{crop.description}</p>
                    <hr />
                  </div>
                ))
              ) : (
                <p>No suitable crops found for this season.</p>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default App;
