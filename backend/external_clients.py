from __future__ import annotations

from typing import Any

import requests

from backend.config import EXTERNAL_API_TIMEOUT_SECONDS, OPENWEATHER_API_KEY, TOMTOM_API_KEY

OPENWEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"
TOMTOM_URL = "https://api.tomtom.com/traffic/services/4/flowSegmentData/absolute/10/json"


class ExternalDataError(RuntimeError):
    pass


def validate_external_keys() -> None:
    if not OPENWEATHER_API_KEY or not TOMTOM_API_KEY:
        raise ExternalDataError("Missing OPENWEATHER_API_KEY or TOMTOM_API_KEY")


def fetch_weather(lat: float, lon: float) -> dict[str, Any]:
    response = requests.get(
        OPENWEATHER_URL,
        params={"lat": lat, "lon": lon, "appid": OPENWEATHER_API_KEY, "units": "metric"},
        timeout=EXTERNAL_API_TIMEOUT_SECONDS,
    )
    response.raise_for_status()

    payload = response.json()
    if "main" not in payload:
        raise ExternalDataError("Weather payload is missing 'main'")

    return {
        "temp": float(payload["main"]["temp"]),
        "visibility": float(payload.get("visibility", 10000)),
        "rain": 1 if "rain" in payload else 0,
    }


def fetch_traffic_stress(lat: float, lon: float) -> float:
    response = requests.get(
        TOMTOM_URL,
        params={"point": f"{lat},{lon}", "key": TOMTOM_API_KEY},
        timeout=EXTERNAL_API_TIMEOUT_SECONDS,
    )
    response.raise_for_status()

    payload = response.json()
    segment = payload.get("flowSegmentData")
    if not segment:
        return 0.2

    speed = max(float(segment.get("currentSpeed", 1)), 1)
    free_flow = max(float(segment.get("freeFlowSpeed", 1)), 1)
    return max(0.0, min(1.0, 1 - (speed / free_flow)))

