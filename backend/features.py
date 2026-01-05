import pandas as pd
from datetime import datetime

# -----------------------------
# Static city-wide defaults
# -----------------------------
DEFAULT_LANES = 2
DEFAULT_SPEED_LIMIT = 40   # km/h
DEFAULT_INTERSECTION = 0   # unknown → assume non-intersection

# Peak hour logic
RUSH_HOURS = {7, 8, 9, 16, 17, 18}

def build_features(
    lat,
    lon,
    weather,
    traffic_stress,
    accident_density
):
    now = datetime.utcnow()

    hour = now.hour
    day_of_week = now.weekday()
    month = now.month

    is_weekend = int(day_of_week >= 5)
    is_night = int(hour >= 20 or hour <= 5)
    is_rush_hour = int(hour in RUSH_HOURS)

    lanes = DEFAULT_LANES
    speed_limit = DEFAULT_SPEED_LIMIT
    is_intersection = DEFAULT_INTERSECTION

    night_intersection_risk = int(is_night and is_intersection)
    highspeed_night = int(is_night and speed_limit >= 50)

    return {
        "temp": weather["temp"],
        "visibility": weather["visibility"],
        "rain": weather["rain"],
        "traffic_stress": traffic_stress,

        "hour": hour,
        "day_of_week": day_of_week,
        "month": month,
        "is_weekend": is_weekend,
        "is_night": is_night,
        "is_rush_hour": is_rush_hour,

        "lanes": lanes,
        "speed_limit": speed_limit,
        "is_intersection": is_intersection,

        "accident_density": accident_density,
        "night_intersection_risk": night_intersection_risk,
        "highspeed_night": highspeed_night
    }

def build_dataframe(feature_rows):
    df = pd.DataFrame(feature_rows)

    # Ensure column order matches training
    ordered_columns = [
        "temp",
        "visibility",
        "rain",
        "traffic_stress",
        "hour",
        "day_of_week",
        "month",
        "is_weekend",
        "is_night",
        "is_rush_hour",
        "lanes",
        "speed_limit",
        "is_intersection",
        "accident_density",
        "night_intersection_risk",
        "highspeed_night",
    ]

    return df[ordered_columns]
