import requests
import pandas as pd
import time

OVERPASS_URL = "https://overpass-api.de/api/interpreter"

df = pd.read_csv("data/raw/accidents.csv").head(800)

road_features = []
failed = 0

headers = {
    "Accept": "application/json",
    "User-Agent": "road-accident-risk/1.0 (learning project)"
}

for idx, r in df.iterrows():
    query = f"""
    [out:json];
    way(around:30,{r.latitude},{r.longitude})["highway"];
    out tags;
    """

    try:
        resp = requests.post(
            OVERPASS_URL,
            data=query,
            headers=headers,
            timeout=30
        )

        # 🔒 Validate response
        if resp.status_code != 200 or not resp.text.strip().startswith("{"):
            failed += 1
            time.sleep(1)
            road_features.append({
                "lanes": 1,
                "speed_limit": 30,
                "is_intersection": 0
            })
            continue

        res = resp.json()

        if "elements" not in res or len(res["elements"]) == 0:
            road_features.append({
                "lanes": 1,
                "speed_limit": 30,
                "is_intersection": 0
            })
        else:
            tags = res["elements"][0].get("tags", {})

            lanes = tags.get("lanes", 1)
            try:
                lanes = int(lanes)
            except:
                lanes = 1

            speed = tags.get("maxspeed", "30")
            try:
                speed = int(speed.split()[0])
            except:
                speed = 30

            road_features.append({
                "lanes": lanes,
                "speed_limit": speed,
                "is_intersection": 1 if "junction" in tags else 0
            })

        time.sleep(1.2)  # 🚦 VERY IMPORTANT for Overpass

    except Exception:
        failed += 1
        road_features.append({
            "lanes": 1,
            "speed_limit": 30,
            "is_intersection": 0
        })
        time.sleep(1.5)

pd.DataFrame(road_features).to_csv("data/raw/roads.csv", index=False)

print(f"Road features saved: {len(road_features)} rows")
print(f"Failed Overpass queries handled safely: {failed}")
