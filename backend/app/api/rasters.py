from fastapi import APIRouter
from fastapi.responses import Response
import base64

router = APIRouter()

# For now return a tiny 2x2 grayscale PNG (placeholder). Replace with real render.
_TINY_PNG = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAIAAAACCAYAAABytg0kAAAAF0lEQVQImWP8//8/AwMDAxgYGAEwAQAJpwO6i3Qq6QAAAABJRU5ErkJggg=="
)

@router.get("/region/{save_id}/layer")
def region_layer(save_id: str, layer: str, season: int):
    return Response(content=_TINY_PNG, media_type="image/png")

@router.get("/farm/{save_id}/raster")
def farm_raster(save_id: str, layer: str, season: int | None = None):
    return Response(content=_TINY_PNG, media_type="image/png")