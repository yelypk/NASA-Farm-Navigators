from fastapi import APIRouter
from ..store import saves

router = APIRouter()

@router.get("/events/{save_id}/season")
def list_events(save_id: str):
    # Stub: return any queued events in save
    return saves.get_events(save_id)

@router.post("/events/{save_id}/{event_key}/resolve")
def resolve_event(save_id: str, event_key: str, choice: dict):
    return saves.resolve_event(save_id, event_key, choice)