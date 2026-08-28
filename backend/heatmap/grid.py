import numpy as np
from backend.config import GRID_RESOLUTION, NYC_BOUNDS

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
