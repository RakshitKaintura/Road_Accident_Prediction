import joblib
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "model" / "xgb_model.pkl"

model = joblib.load(MODEL_PATH)
