import React, { useState } from "react";
import axios from "axios";
import "./styles.css"; // Import CSS

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

  // Get Image Path for Crops
  const getImagePath = (cropName) => `/crop_images/${cropName.toLowerCase().replace(/\s/g, "")}.jpg`;

  // Fetch Weather Data
  const fetchWeather = async () => {
    try {
      const response = await axios.get(`http://127.0.0.1:5001/weather/?district=${district}`);
      setWeatherData(response.data);
    } catch (error) {
      console.error("Error fetching weather data:", error);
    }
  };

  // Predict Crops
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
    <div className="container">
      <h1>🌾 Crop Prediction App</h1>

      {/* District Input */}
      <label>Enter District: </label>
      <input type="text" value={district} onChange={(e) => setDistrict(e.target.value)} />

      {/* Input Fields */}
      <h3>Enter Soil Conditions:</h3>
      <p>Nitrogen: <input type="number" name="N" value={inputs.N} onChange={handleChange} placeholder="Nitrogen (mg/kg)" /></p>
      <p>Phosphorus: <input type="number" name="P" value={inputs.P} onChange={handleChange} placeholder="Phosphorus (mg/kg)" /></p>
      <p>Potassium: <input type="number" name="K" value={inputs.K} onChange={handleChange} placeholder="Potassium (mg/kg)" /></p>
      <p>pH: <input type="number" name="ph" value={inputs.ph} onChange={handleChange} placeholder="pH Level" /></p>

      {/* Action Buttons */}
      <button onClick={fetchWeather}>🌦 Get Weather Data</button>
      <button onClick={predictCrops}>🌱 Predict Crops</button>

      {/* Weather Data Display */}
      {weatherData && (
        <div className="weather-section">
          <h2>🌦 Seasonal Weather Data</h2>
          {Object.entries(weatherData).map(([season, values]) => (
            <div key={season} className="card">
              <h3>📅 {season} Season</h3>
              <p>🌡 Temperature: {values.temperature}</p>
              <p>💧 Humidity: {values.humidity}</p>
              <p>🌧 Rainfall: {values.rainfall} mm</p>
            </div>
          ))}
        </div>
      )}

      {/* Crop Predictions */}
      {cropPredictions && (
        <div className="crop-section">
          <h2>🌱 Recommended Crops</h2>
          {Object.entries(cropPredictions).map(([season, crops]) => (
            <div key={season}>
              <h3 className="season-title">📅 {season} Season</h3>
              <div className="crop-grid">
                {crops.length > 0 ? (
                  crops.map((crop, index) => (
                    <div key={index} className="card">
                      <img src={getImagePath(crop.name)} alt={crop.name} className="crop-image" />
                      <h4>🌾 {crop.name}</h4>
                      <p><strong>Soil Type:</strong> {crop.soil_type}</p>
                      <p><strong>Yield:</strong> {crop.min_yield} - {crop.max_yield} tons</p>
                      <p><strong>Price:</strong> ₹{crop.min_price} - ₹{crop.max_price} per kg</p>
                      <p><strong>Fertilizer:</strong> {crop.fertilizer}</p>
                      <p>{crop.description}</p>
                    </div>
                  ))
                ) : (
                  <p>No suitable crops found for this season.</p>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default App;
