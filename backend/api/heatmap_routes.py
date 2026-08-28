from fastapi import APIRouter

from backend.heatmap.generator import generate_city_heatmap
from backend.schemas import HeatmapResponse

router = APIRouter()


@router.get("/heatmap", response_model=HeatmapResponse, tags=["prediction"])
def heatmap() -> HeatmapResponse:
    return generate_city_heatmap()
