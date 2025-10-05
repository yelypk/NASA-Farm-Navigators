from typing import List, Literal, Optional, Tuple, Dict, Any
from pydantic import BaseModel, Field

Season = Literal["S1","S2","S3","S4"]

class Cell(BaseModel):
    x: int
    y: int

class AssignCrop(BaseModel):
    cell: Tuple[int,int]
    crop: str

class IrrigationPlan(BaseModel):
    rate_mm: float = 0.0
    area_mask: List[Tuple[int,int]] = []

class PlanCrops(BaseModel):
    assign: List[AssignCrop] = []
    irrigation: Optional[IrrigationPlan] = None
    mulch: bool = False
    cover_crop: List[Dict[str, Any]] = []  # {"fieldId": int, "type": str}

class Herd(BaseModel):
    species: Literal["cattle","goat","sheep"]
    head: int

class HerdMove(BaseModel):
    herd: int
    cells: List[Tuple[int,int]]

class PlanLivestock(BaseModel):
    herds: List[Herd] = []
    moves: List[HerdMove] = []
    feed: Dict[str, float] = {}  # {"hay_t": 2.5}

class DrainageBuild(BaseModel):
    type: Literal["ditch","tile"]
    cells: List[Tuple[int,int]]

class PlanDrainage(BaseModel):
    build: List[DrainageBuild] = []
    flush: bool = False

class PlanPests(BaseModel):
    chem: Dict[str, Any] = {}
    bio: Dict[str, Any] = {}
    scouting: bool = False

class SaveState(BaseModel):
    id: str
    scenario: str
    year: int
    season: Season
    resources: Dict[str, Any] = {}
    farm: Dict[str, Any] = {}

class DeltaSeason(BaseModel):
    yield_: List[Dict[str, Any]] = Field(default_factory=list, alias="yield")
    soil: Dict[str, Any] = {}
    water: Dict[str, Any] = {}
    pests: Dict[str, Any] = {}
    finance: Dict[str, Any] = {}

class TickResult(BaseModel):
    year: int
    season: Season
    deltas: DeltaSeason
    ndvi_patch_png: str = ""

class EventOption(BaseModel):
    key: str
    title: str
    effects: Dict[str, Any] = {}

class Event(BaseModel):
    key: str
    title: str
    options: List[EventOption]

class FinanceReport(BaseModel):
    revenue: float = 0
    opex: float = 0
    capex: float = 0
    loans: List[Dict[str, Any]] = []