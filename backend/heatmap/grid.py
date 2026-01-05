import numpy as np

NYC_BOUNDS = {
    "lat_min": 40.49,
    "lat_max": 40.92,
    "lon_min": -74.27,
    "lon_max": -73.68
}

GRID_RESOLUTION = 0.003  # ~300m

def generate_city_grid():
    lat_vals = np.arange(
        NYC_BOUNDS["lat_min"],
        NYC_BOUNDS["lat_max"],
        GRID_RESOLUTION
    )
    lon_vals = np.arange(
        NYC_BOUNDS["lon_min"],
        NYC_BOUNDS["lon_max"],
        GRID_RESOLUTION
    )

    return [(float(lat), float(lon)) for lat in lat_vals for lon in lon_vals]
