from __future__ import annotations

from datetime import datetime

import requests
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from backend.api.heatmap_routes import router as heatmap_router
from backend.config import BACKEND_CORS_ORIGINS, CACHE_TTL_SECONDS, RISK_THRESHOLD
from backend.external_clients import (
    ExternalDataError,
    fetch_traffic_stress,
    fetch_weather,
    validate_external_keys,
)
from backend.features import build_dataframe, build_features
from backend.model import model
from backend.schemas import HealthResponse, PredictResponse

THRESHOLD = RISK_THRESHOLD

app = FastAPI(
    title="Road Accident Risk API",
    description="Predict road accident severity risk and generate city heatmaps.",
    version="1.1.0",
)
app.include_router(heatmap_router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", response_model=HealthResponse, tags=["system"])
def health() -> HealthResponse:
    return HealthResponse(
        status="ok",
        generated_at=datetime.utcnow(),
        model_loaded=model is not None,
        cache_ttl_seconds=CACHE_TTL_SECONDS,
    )


@app.get("/predict", response_model=PredictResponse, tags=["prediction"])
def predict(
    lat: float = Query(..., ge=-90, le=90, description="Latitude"),
    lon: float = Query(..., ge=-180, le=180, description="Longitude"),
) -> PredictResponse:
    try:
        validate_external_keys()
        weather = fetch_weather(lat, lon)
        traffic_stress = fetch_traffic_stress(lat, lon)
    except requests.RequestException as exc:
        raise HTTPException(status_code=502, detail=f"External API request failed: {exc}") from exc
    except ExternalDataError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    row = build_features(
        lat=lat,
        lon=lon,
        weather=weather,
        traffic_stress=traffic_stress,
        accident_density=0.3,
    )
    proba = float(model.predict_proba(build_dataframe([row]))[0][1])
    severe_risk = int(proba > THRESHOLD)

    risk_label = "High" if proba >= 0.7 else "Medium" if proba >= THRESHOLD else "Low"

    return PredictResponse(
        severe_risk=severe_risk,
        probability=round(proba, 3),
        threshold=THRESHOLD,
        risk_label=risk_label,
    )