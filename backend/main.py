from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import joblib
import requests
import os
from datetime import datetime

from config import OPENWEATHER_API_KEY, TOMTOM_API_KEY

# ---------------- APP SETUP ----------------
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------- LOAD MODEL ----------------
BASE_DIR = os.path.dirname(__file__)
model = joblib.load(os.path.join(BASE_DIR, "model", "xgb_model.pkl"))

THRESHOLD = 0.35  # tuned for recall

# ---------------- PREDICTION API ----------------
@app.get("/predict")
def predict(lat: float, lon: float):

    # -------- Weather API --------
    w = requests.get(
        "https://api.openweathermap.org/data/2.5/weather",
        params={
            "lat": lat,
            "lon": lon,
            "appid": OPENWEATHER_API_KEY,
            "units": "metric",
        },
        timeout=10,
    ).json()

    # -------- Traffic API --------
    t = requests.get(
        "https://api.tomtom.com/traffic/services/4/flowSegmentData/absolute/10/json",
        params={
            "point": f"{lat},{lon}",
            "key": TOMTOM_API_KEY,
        },
        timeout=10,
    ).json()

    # -------- Defensive Checks --------
    if "main" not in w or "flowSegmentData" not in t:
        return {"error": "External API failure"}

    # -------- Feature Engineering (INFERENCE) --------
    temp = w["main"]["temp"]
    visibility = w.get("visibility", 0)
    rain = 1 if "rain" in w else 0

    speed = t["flowSegmentData"]["currentSpeed"]
    free_flow = max(t["flowSegmentData"]["freeFlowSpeed"], 1)

    # Traffic stress (same as training)
    traffic_stress = max(0, min(1, 1 - (speed / free_flow)))

    # ⚠️ NOTE:
    # Features like time, road structure, accident_density
    # are learned historically by the model.
    # At inference, we pass only dynamic features.
    now = datetime.now()

    hour = now.hour
    day_of_week = now.weekday()
    month = now.month

    is_weekend = int(day_of_week >= 5)
    is_night = int(hour >= 20 or hour <= 5)
    is_rush_hour = int(hour in [7,8,9,16,17,18])

    X = [[
    temp,
    visibility,
    rain,
    traffic_stress,
    hour,
    day_of_week,
    month,
    is_weekend,
    is_night,
    is_rush_hour
]]


    # -------- Prediction --------
    proba = model.predict_proba(X)[0][1]
    severe_risk = int(proba > THRESHOLD)

    return {
        "severe_risk": severe_risk,
        "probability": round(float(proba), 3),
        "threshold": THRESHOLD
    }
