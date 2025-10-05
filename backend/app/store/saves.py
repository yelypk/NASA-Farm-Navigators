from __future__ import annotations
from typing import Dict, Any
from dataclasses import dataclass
import uuid

from ..models import SaveState, DeltaSeason

@dataclass
class SaveData:
    state: SaveState
    plans: Dict[str, Any]
    events: list
    finance: Dict[str, Any]

_DB: Dict[str, SaveData] = {}

def new_game(scenario: str) -> SaveState:
    sid = uuid.uuid4().hex[:8]
    state = SaveState(id=sid, scenario=scenario, year=1, season="S1", resources={"money": 10000}, farm={"size_km": 1})
    _DB[sid] = SaveData(state=state, plans={}, events=[], finance={"loans": [], "insurances": []})
    return state

def get_state(save_id: str) -> SaveState:
    return _DB[save_id].state

def get_plans(save_id: str) -> Dict[str, Any]:
    return _DB[save_id].plans

def save_plan(save_id: str, kind: str, payload: Dict[str, Any]):
    _DB[save_id].plans[kind] = payload
    return {"ok": True, "kind": kind}

def get_events(save_id: str):
    return _DB[save_id].events

def resolve_event(save_id: str, key: str, choice: dict):
    # Remove event and record choice (stub)
    evs = _DB[save_id].events
    _DB[save_id].events = [e for e in evs if e.get("key") != key]
    return {"resolved": key, "choice": choice}

def add_loan(save_id: str, loan: dict):
    _DB[save_id].finance.setdefault("loans", []).append(loan)
    return {"ok": True}

def add_insurance(save_id: str, ins: dict):
    _DB[save_id].finance.setdefault("insurances", []).append(ins)
    return {"ok": True}

def finance_report(save_id: str, year: int | None):
    # Stub report
    fin = _DB[save_id].finance
    return {"revenue": 0, "opex": 0, "capex": 0, "loans": fin.get("loans", [])}

def advance_time(save_id: str, deltas: DeltaSeason) -> SaveState:
    s = _DB[save_id].state
    # naive season advance
    s_map = ["S1", "S2", "S3", "S4"]
    i = s_map.index(s.season)
    if i < 3:
        s.season = s_map[i+1]
    else:
        s.season = "S1"
        s.year += 1
    return s