import os
from dotenv import load_dotenv

load_dotenv()

OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
TOMTOM_API_KEY = os.getenv("TOMTOM_API_KEY")

# NYC bounding box
NYC_BOUNDS = {
    "lat_min": 40.49,
    "lat_max": 40.92,
    "lon_min": -74.27,
    "lon_max": -73.68
}

GRID_RESOLUTION = 0.003   # ~300m
RISK_THRESHOLD = 0.3
CACHE_TTL_SECONDS = 600  # 10 minutes
