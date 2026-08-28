from __future__ import annotations

import math
from datetime import datetime

import requests

from backend.cache import get_cache, set_cache
from backend.config import CACHE_TTL_SECONDS, HEATMAP_MAX_POINTS, NYC_BOUNDS, RISK_THRESHOLD
from backend.external_clients import (
    ExternalDataError,
    fetch_traffic_stress,
    fetch_weather,
    validate_external_keys,
)
from backend.features import build_dataframe, build_features
from backend.heatmap.grid import generate_city_grid
from backend.model import model


def _sample_grid_points(coords: list[tuple[float, float]], max_points: int) -> list[tuple[float, float]]:
    if max_points <= 0 or len(coords) <= max_points:
        return coords

    step = max(1, len(coords) // max_points)
    sampled = coords[::step]
    return sampled[:max_points]


def _normalized_distance(lat: float, lon: float) -> float:
    center_lat = (NYC_BOUNDS["lat_min"] + NYC_BOUNDS["lat_max"]) / 2
    center_lon = (NYC_BOUNDS["lon_min"] + NYC_BOUNDS["lon_max"]) / 2

    lat_span = max(NYC_BOUNDS["lat_max"] - NYC_BOUNDS["lat_min"], 1e-6)
    lon_span = max(NYC_BOUNDS["lon_max"] - NYC_BOUNDS["lon_min"], 1e-6)

    dlat = (lat - center_lat) / lat_span
    dlon = (lon - center_lon) / lon_span
    return math.sqrt(dlat * dlat + dlon * dlon)


def get_accident_density(lat: float, lon: float) -> float:
    dist = _normalized_distance(lat, lon)
    center_boost = max(0.0, 1 - dist * 1.9)
    wave = 0.1 * (math.sin(lat * 25) + math.cos(lon * 25))
    density = 0.18 + (0.45 * center_boost) + wave
    return max(0.05, min(0.95, round(density, 3)))


def generate_city_heatmap() -> dict:
    now_iso = datetime.utcnow().isoformat()

    try:
        validate_external_keys()
    except ExternalDataError as exc:
        return {
            "generated_at": now_iso,
            "points": [],
            "total_points": 0,
            "source_points_evaluated": 0,
            "threshold": RISK_THRESHOLD,
            "used_cache": False,
            "error": str(exc),
        }

    cached = get_cache("city_heatmap")
    if cached:
        cached_with_flag = dict(cached)
        cached_with_flag["used_cache"] = True
        return cached_with_flag

    coords = _sample_grid_points(generate_city_grid(), HEATMAP_MAX_POINTS)

    # Keep heatmap generation fast: fetch live context once and reuse across the grid.
    center_lat = (NYC_BOUNDS["lat_min"] + NYC_BOUNDS["lat_max"]) / 2
    center_lon = (NYC_BOUNDS["lon_min"] + NYC_BOUNDS["lon_max"]) / 2
    try:
        weather = fetch_weather(center_lat, center_lon)
        base_traffic_stress = fetch_traffic_stress(center_lat, center_lon)
    except (requests.RequestException, ExternalDataError, ValueError) as exc:
        return {
            "generated_at": now_iso,
            "points": [],
            "total_points": 0,
            "source_points_evaluated": len(coords),
            "threshold": RISK_THRESHOLD,
            "used_cache": False,
            "error": f"Unable to fetch live context: {exc}",
        }

    rows: list[dict] = []
    row_coords: list[tuple[float, float]] = []

    for lat, lon in coords:
        # Small deterministic spatial variation keeps the heatmap expressive.
        traffic_variation = 0.08 * math.sin((lat + lon) * 18)
        traffic_stress = max(0.0, min(1.0, base_traffic_stress + traffic_variation))
        row = build_features(
            lat=lat,
            lon=lon,
            weather=weather,
            traffic_stress=traffic_stress,
            accident_density=get_accident_density(lat, lon),
        )
        row_coords.append((lat, lon))
        rows.append(row)

    probs = model.predict_proba(build_dataframe(rows))[:, 1]

    points = []
    for (lat, lon), probability in zip(row_coords, probs):
        # Always return points so the UI has a continuous risk surface.
        intensity = float(probability)
        points.append(
            {
                "lat": lat,
                "lng": lon,
                "risk": max(0.05, round(float(intensity), 3)),
            }
        )

    response = {
        "generated_at": now_iso,
        "total_points": len(points),
        "points": points,
        "source_points_evaluated": len(coords),
        "threshold": RISK_THRESHOLD,
        "used_cache": False,
        "error": None,
    }
    set_cache("city_heatmap", response, CACHE_TTL_SECONDS)
    return response
