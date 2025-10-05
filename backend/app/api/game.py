from fastapi import APIRouter
from pydantic import BaseModel
from ..models import SaveState

from ..store import saves

router = APIRouter()

class NewGameReq(BaseModel):
    scenario: str

@router.post("/game/new", response_model=SaveState)
def new_game(req: NewGameReq):
    return saves.new_game(req.scenario)

@router.get("/game/{save_id}/state", response_model=SaveState)
def get_state(save_id: str):
    return saves.get_state(save_id)