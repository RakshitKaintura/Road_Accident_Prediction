import requests
import os
import pandas as pd
import time
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("TOMTOM_API_KEY")

if API_KEY is None:
    raise ValueError("TOMTOM_API_KEY not found in .env")

df = pd.read_csv("data/raw/accidents.csv").head(1000)

traffic_rows = []
failed = 0

for idx, r in df.iterrows():
    try:
        url = "https://api.tomtom.com/traffic/services/4/flowSegmentData/absolute/10/json"
        params = {
            "point": f"{r.latitude},{r.longitude}",
            "key": API_KEY
        }

        res = requests.get(url, params=params, timeout=10).json()

        # 🔒 VALIDATION
        if "flowSegmentData" not in res:
            failed += 1
            continue

        seg = res["flowSegmentData"]

        traffic_rows.append({
            "speed": seg.get("currentSpeed", 0),
            "free_flow": seg.get("freeFlowSpeed", 1)
        })

        time.sleep(0.2)  # 🚦 rate-limit protection

    except Exception:
        failed += 1
        continue

traffic_df = pd.DataFrame(traffic_rows)
traffic_df.to_csv("data/raw/traffic.csv", index=False)

print(f"Traffic data saved: {len(traffic_df)} rows")
print(f"Failed traffic points skipped: {failed}")
