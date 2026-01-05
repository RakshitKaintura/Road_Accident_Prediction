from fastapi import APIRouter
from backend.heatmap.generator import generate_city_heatmap

router = APIRouter()

@router.get("/heatmap")
def get_heatmap():
    return generate_city_heatmap()
