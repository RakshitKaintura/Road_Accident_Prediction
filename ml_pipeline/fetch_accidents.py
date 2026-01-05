import pandas as pd

URL = "https://data.cityofnewyork.us/resource/h9gi-nx95.csv?$limit=50000"

df = pd.read_csv(URL)

df = df[
    [
        "crash_date",
        "crash_time",
        "latitude",
        "longitude",
        "number_of_persons_injured",
        "number_of_persons_killed",
    ]
]

df.dropna(inplace=True)

# ---------------- ORIGINAL SEVERITY ----------------
def label(row):
    if row["number_of_persons_killed"] > 0:
        return 2
    elif row["number_of_persons_injured"] > 0:
        return 1
    return 0

df["severity"] = df.apply(label, axis=1)

# ---------------- BINARY TARGET ----------------
df["severe"] = (df["severity"] > 0).astype(int)

# ---------------- 🔥 SPATIAL GRID ----------------
# ~100m grid resolution
df["lat_bin"] = (df["latitude"] * 100).astype(int)
df["lon_bin"] = (df["longitude"] * 100).astype(int)

# ---------------- 🔥 STABLE RISK ----------------
df["accident_density"] = (
    df.groupby(["lat_bin", "lon_bin"])["severe"]
    .transform("mean")
)

df.to_csv("data/raw/accidents.csv", index=False)
print("Accidents fetched with spatial grid risk")
