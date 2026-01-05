import numpy as np
import requests
from datetime import datetime

from app.config import *
from app.model import predict_proba
from app.features import build_features, build_dataframe
from app.cache import get_cache, set_cache

# -----------------------------
# Grid Generator
# -----------------------------
def generate_grid():
    lat_vals = np.arange(NYC_BOUNDS["lat_min"], NYC_BOUNDS["lat_max"], GRID_RESOLUTION)
    lon_vals = np.arange(NYC_BOUNDS["lon_min"], NYC_BOUNDS["lon_max"], GRID_RESOLUTION)
    return [(lat, lon) for lat in lat_vals for lon in lon_vals]

# -----------------------------
# External APIs
# -----------------------------
def fetch_weather(lat, lon):
    url = (
        "https://api.openweathermap.org/data/2.5/weather"
        f"?lat={lat}&lon={lon}&appid={OPENWEATHER_API_KEY}&units=metric"
    )
    r = requests.get(url, timeout=5).json()

    return {
        "temp": r["main"]["temp"],
        "visibility": r.get("visibility", 10000),
        "rain": r.get("rain", {}).get("1h", 0)
    }

def fetch_traffic_stress(lat, lon):
    url = (
        "https://api.tomtom.com/traffic/services/4/flowSegmentData/absolute/10/json"
        f"?point={lat},{lon}&key={TOMTOM_API_KEY}"
    )
    r = requests.get(url, timeout=5).json()

    # Normalize confidence to 0–1 stress
    confidence = r["flowSegmentData"].get("confidence", 0.5)
    return min(max(1 - confidence, 0), 1)

# -----------------------------
# Spatial Accident Density
# -----------------------------
def compute_accident_density(lat, lon):
    """
    Replace this later with:
    - KDE
    - H3 aggregation
    - DBSCAN cluster density

    For now: safe proxy
    """
    return 0.3  # baseline NYC risk

# -----------------------------
# Heatmap Generator
# -----------------------------
def generate_heatmap():
    cache_key = "nyc_severe_risk_heatmap"
    cached = get_cache(cache_key)
    if cached:
        return cached

    grid = generate_grid()

    feature_rows = []
    coords = []

    for lat, lon in grid:
        try:
            weather = fetch_weather(lat, lon)
            traffic_stress = fetch_traffic_stress(lat, lon)
            accident_density = compute_accident_density(lat, lon)

            row = build_features(
                lat,
                lon,
                weather,
                traffic_stress,
                accident_density
            )

            feature_rows.append(row)
            coords.append((lat, lon))

        except Exception:
            continue

    df = build_dataframe(feature_rows)
    probs = predict_proba(df)

    points = []
    for (lat, lon), p in zip(coords, probs):
        if p >= RISK_THRESHOLD:
            intensity = (p - RISK_THRESHOLD) / (1 - RISK_THRESHOLD)
            points.append({
                "lat": lat,
                "lng": lon,
                "risk": round(float(intensity), 3)
            })

    response = {
        "generated_at": datetime.utcnow().isoformat(),
        "grid_points": len(points),
        "points": points
    }

    set_cache(cache_key, response, CACHE_TTL_SECONDS)
    return response
