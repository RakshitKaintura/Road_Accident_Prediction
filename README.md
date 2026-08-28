# 🚦 Road Accident Risk Intelligence Platform

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.95+-009688.svg)
![React](https://img.shields.io/badge/React-18.2+-61DAFB.svg)
![Machine Learning](https://img.shields.io/badge/ML-XGBoost-orange.svg)

A full-stack machine learning product that predicts severe road accident risk and renders a live, city-scale heatmap for operational decision-making. 

This platform bridges the gap between raw data and actionable intelligence by consuming various real-time datasets (weather, traffic, road infrastructure), feeding them into a trained ML model, and visualizing the risk via an interactive dashboard.

---

## ✨ Key Features

- **End-to-End ML Pipeline**: From automated data ingestion and feature engineering to model training and API serving.
- **Production-Ready Backend**: Features strongly-typed API contracts, robust input validation, cache-aware heatmap generation, and resilient external API fault handling.
- **Interactive Geospatial UI**: A sleek, recruiter-friendly React frontend offering live metrics, dynamic risk filtering controls, responsive design, and polished map visualizations.
- **Real-Time Data Integration**: Merges insights from OpenWeather, TomTom traffic, and public accident/road datasets for highly accurate predictions.

## 🛠️ Technology Stack

| Component | Technologies Used |
| :--- | :--- |
| **Backend** | FastAPI, Python, Pydantic, Uvicorn |
| **Machine Learning** | XGBoost, Pandas, NumPy, Scikit-learn |
| **Frontend** | React, Google Maps Maps JavaScript API (Heatmap Layer), CSS |
| **Data Sources** | OpenWeather API, TomTom API, Public accident datasets |

## 📁 Project Structure

```text
road-accident-risk/
├── backend/          # FastAPI service providing `/predict`, `/heatmap`, and `/health`
├── frontend/         # React dashboard for risk visualization and controls
├── ml_pipeline/      # Data collection, dataset build, and training scripts
└── data/             # Raw and processed datasets (ignored in git)
```

## 🚀 Getting Started

Follow these steps to run the platform locally.

### Backend Setup

1. **Set up the virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```
2. **Install dependencies:**
   ```bash
   pip install -r backend/requirements.txt
   ```
3. **Configure Environment Variables:**
   Copy `.env.example` to `.env` in the root directory and add your API keys:
   ```env
   OPENWEATHER_API_KEY=your_api_key_here
   TOMTOM_API_KEY=your_api_key_here
   BACKEND_CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
   ```
4. **Run the API:**
   ```bash
   uvicorn backend.main:app --reload --port 8000
   ```
   *The API will be available at `http://127.0.0.1:8000`*

### Frontend Setup

1. **Install dependencies:**
   ```bash
   cd frontend
   npm install
   ```
2. **Configure Environment Variables:**
   Copy `frontend/.env.example` to `frontend/.env` and add your Google Maps key:
   ```env
   REACT_APP_GOOGLE_MAPS_API_KEY=your_google_maps_api_key
   REACT_APP_BACKEND_URL=http://127.0.0.1:8000
   ```
3. **Run the application:**
   ```bash
   npm start
   ```
   *The frontend will start at `http://localhost:3000`*

## 🔌 API Endpoints

The FastAPI backend exposes the following key endpoints:

- `GET /health` : Service health status, model readiness state, and cache TTL.
- `GET /predict?lat=...&lon=...` : Returns severe-risk classification and probability for a specific location.
- `GET /heatmap` : Returns cached city heatmap data points and metadata for map rendering.

## 🧠 ML Pipeline Execution Order

To retrain the model or fetch fresh data, run these scripts from the repository root in order:

1. `python ml_pipeline/fetch_accidents.py` - Download historical accident data
2. `python ml_pipeline/fetch_weather.py` - Gather historical weather data
3. `python ml_pipeline/fetch_traffic.py` - Retrieve traffic patterns
4. `python ml_pipeline/fetch_roads.py` - Map road infrastructure
5. `python ml_pipeline/build_dataset.py` - Merge and engineer features
6. `python ml_pipeline/train_model.py` - Train the XGBoost model and save artifacts

## 🎯 Suggested Demo Flow (for Recruiters & Stakeholders)

1. **Verify Health**: Navigate to `/health` to demonstrate runtime status and model readiness.
2. **Single Prediction**: Run a `/predict` query with sample coordinates and explain the returned risk probability and contributing factors.
3. **Visual Dashboard**: Open the frontend UI and adjust minimum risk/radius controls live to show responsiveness.
4. **Architecture Overview**: Explain the cache-aware heatmap generation and how the geospatial inference pipeline operates under load.

---
*Built with ❤️ for safer roads.*