import requests, os, pandas as pd
from dotenv import load_dotenv

load_dotenv()
KEY = os.getenv("OPENWEATHER_API_KEY")

df = pd.read_csv("data/raw/accidents.csv").head(3000)

rows = []
for _, r in df.iterrows():
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={r.latitude}&lon={r.longitude}&appid={KEY}"
    res = requests.get(url).json()
    rows.append({
        "temp": res["main"]["temp"],
        "visibility": res.get("visibility", 0),
        "rain": 1 if "rain" in res else 0
    })

weather = pd.DataFrame(rows)
weather.to_csv("data/raw/weather.csv", index=False)
print("Weather saved")
