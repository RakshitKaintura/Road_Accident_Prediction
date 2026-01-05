from datetime import datetime
from backend.heatmap.grid import generate_city_grid
from backend.features import build_features, build_dataframe
from backend.model import model
from backend.utils.weather import get_weather
from backend.utils.traffic import get_traffic_stress

# ---------------------------
# Config
# ---------------------------
RISK_THRESHOLD = 0.3
CACHE_TTL = 600  # seconds

_cache = {}

def _get_cache(key):
    item = _cache.get(key)
    if not item:
        return None
    data, expiry = item
    if expiry < datetime.utcnow().timestamp():
        del _cache[key]
        return None
    return data

def _set_cache(key, value):
    _cache[key] = (value, datetime.utcnow().timestamp() + CACHE_TTL)

# ---------------------------
# Temporary spatial proxy
# ---------------------------
def get_accident_density(lat, lon):
    # TEMP placeholder – upgraded later
    return 0.3

# ---------------------------
# Main generator
# ---------------------------
def generate_city_heatmap():
    cached = _get_cache("city_heatmap")
    if cached:
        return cached

    grid = generate_city_grid()
    rows = []
    coords = []

    for lat, lon in grid:
        try:
            weather = get_weather(lat, lon)
            traffic_stress = get_traffic_stress(lat, lon)
            accident_density = get_accident_density(lat, lon)

            row = build_features(
                lat=lat,
                lon=lon,
                weather=weather,
                traffic_stress=traffic_stress,
                accident_density=accident_density
            )

            rows.append(row)
            coords.append((lat, lon))
        except Exception:
            continue

    df = build_dataframe(rows)
    probs = model.predict_proba(df)[:, 1]

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
        "points": points,
        "total_points": len(points)
    }

    _set_cache("city_heatmap", response)
    return response
