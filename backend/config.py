import os
from dotenv import load_dotenv

load_dotenv()

OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
TOMTOM_API_KEY = os.getenv("TOMTOM_API_KEY")
BACKEND_CORS_ORIGINS = [
    origin.strip()
    for origin in os.getenv(
        "BACKEND_CORS_ORIGINS",
        "http://localhost:3000,http://127.0.0.1:3000",
    ).split(",")
    if origin.strip()
]

# Bengaluru bounding box
NYC_BOUNDS = {
    "lat_min": 12.77,
    "lat_max": 13.23,
    "lon_min": 77.38,
    "lon_max": 77.79,
}

GRID_RESOLUTION = 0.003   # ~300m
RISK_THRESHOLD = 0.3
CACHE_TTL_SECONDS = 600  # 10 minutes
HEATMAP_MAX_POINTS = int(os.getenv("HEATMAP_MAX_POINTS", "250"))
HEATMAP_WORKERS = int(os.getenv("HEATMAP_WORKERS", "8"))
EXTERNAL_API_TIMEOUT_SECONDS = int(os.getenv("EXTERNAL_API_TIMEOUT_SECONDS", "10"))
