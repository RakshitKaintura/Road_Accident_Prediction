import pandas as pd

acc = pd.read_csv("data/raw/accidents.csv").head(1500)
weather = pd.read_csv("data/raw/weather.csv")
traffic = pd.read_csv("data/raw/traffic.csv")
roads = pd.read_csv("data/raw/roads.csv")

# ---------------- ALIGN ----------------
min_len = min(len(acc), len(weather), len(traffic), len(roads))

acc = acc.iloc[:min_len].reset_index(drop=True)
weather = weather.iloc[:min_len].reset_index(drop=True)
traffic = traffic.iloc[:min_len].reset_index(drop=True)
roads = roads.iloc[:min_len].reset_index(drop=True)

# ---------------- TIME FEATURES ----------------
acc["crash_datetime"] = pd.to_datetime(
    acc["crash_date"] + " " + acc["crash_time"],
    format="mixed",
    errors="coerce"
)

acc = acc.dropna(subset=["crash_datetime"]).reset_index(drop=True)

acc["hour"] = acc["crash_datetime"].dt.hour
acc["day_of_week"] = acc["crash_datetime"].dt.weekday
acc["month"] = acc["crash_datetime"].dt.month
acc["is_weekend"] = (acc["day_of_week"] >= 5).astype(int)
acc["is_night"] = acc["hour"].isin([20,21,22,23,0,1,2,3,4,5]).astype(int)
acc["is_rush_hour"] = acc["hour"].isin([7,8,9,16,17,18]).astype(int)

# ---------------- MERGE ----------------
df = pd.concat([acc, weather, traffic, roads], axis=1)

# ---------------- TRAFFIC STRESS ----------------
df["traffic_stress"] = (1 - (df["speed"] / df["free_flow"])).clip(0, 1)

# ---------------- INTERACTIONS ----------------
df["night_intersection_risk"] = df["is_night"] * df["is_intersection"]
df["highspeed_night"] = ((df["speed_limit"] > 50).astype(int)) * df["is_night"]

# ---------------- FINAL FEATURES ----------------
features = [
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
    "accident_density",          # 🔥 spatial signal
    "night_intersection_risk",
    "highspeed_night",
    "severe",
]

df = df[features]

df.to_csv("data/processed/train.csv", index=False)
print(f"Spatial-risk dataset ready: {len(df)} rows")
