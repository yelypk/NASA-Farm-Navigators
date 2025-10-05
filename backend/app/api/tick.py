from fastapi import APIRouter
from ..models import TickResult, DeltaSeason
from ..store import saves
from ..sim import tick as sim_tick

router = APIRouter()

@router.post("/tick/{save_id}", response_model=TickResult)
def do_tick(save_id: str):
    state = saves.get_state(save_id)
    plans = saves.get_plans(save_id)
    # Run simulation (stubbed)
    deltas = sim_tick.run(state, plans)
    state = saves.advance_time(save_id, deltas)
    ndvi_patch_png = f"/region/{save_id}/ndvi_patch_t{state.year*4}.png"
    return TickResult(year=state.year, season=state.season, deltas=deltas, ndvi_patch_png=ndvi_patch_png)