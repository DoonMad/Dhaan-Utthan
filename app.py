from flask import Flask
from routes.weather import weather_blueprint
from routes.predict import predict_blueprint
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend integration

# Register Blueprints
app.register_blueprint(weather_blueprint, url_prefix="/weather")
app.register_blueprint(predict_blueprint, url_prefix="/predict")

@app.route("/", methods=["GET"])
def home():
    return {"message": "Welcome to Crop Prediction API!"}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
