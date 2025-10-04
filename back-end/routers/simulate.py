from fastapi import APIRouter
from ..models.dto import TurnIn
from ..services.tiles_repo import TilesRepo
from ..services.state_store import StateStore
from pathlib import Path as _P
import sys as _sys
_sys.path.append(str((_P(__file__).resolve().parents[2] / "dataproc").resolve()))
from simulate.apply_decisions import apply_turn  # type: ignore

router = APIRouter(prefix="/simulate", tags=["simulate"])
repo = TilesRepo()
state = StateStore()

@router.post("/turn")
async def simulate_turn(body: TurnIn):
    tiles = repo.get_year(body.region_id, body.year)
    result = apply_turn(tiles, body.decisions.model_dump(by_alias=True))
    await state.add_year(body.run_id, body.region_id, body.year, result["economy"])
    return result
