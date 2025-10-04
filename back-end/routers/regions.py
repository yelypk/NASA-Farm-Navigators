from fastapi import APIRouter, HTTPException
from ..services.tiles_repo import TilesRepo

router = APIRouter(prefix="/regions", tags=["regions"])
repo = TilesRepo()

@router.get("")
def list_regions():
    return repo.list_regions()

@router.get("/{region_id}/year/{year}")
def get_region_year(region_id: str, year: int):
    try:
        return repo.get_year(region_id, year)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Tile not found")
