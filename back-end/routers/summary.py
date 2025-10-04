from fastapi import APIRouter
from ..services.state_store import StateStore

router = APIRouter(prefix="/summary", tags=["summary"])
state = StateStore()

@router.get("/{run_id}")
async def get_summary(run_id: str):
    return await state.summary(run_id)
