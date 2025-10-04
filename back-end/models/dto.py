from pydantic import BaseModel, Field
from typing import List, Dict, Optional

class GridInfo(BaseModel):
    w: int
    h: int

class Region(BaseModel):
    id: str
    name: str
    years: List[int]
    grid: GridInfo
    layers: List[str]

class TurnDecisions(BaseModel):
    crops: Optional[Dict] = None
    water: Optional[Dict] = None
    soil: Optional[Dict] = None
    finance: Optional[Dict] = None

class TurnIn(BaseModel):
    run_id: str
    region_id: str
    year: int
    decisions: TurnDecisions

class DeltaCell(BaseModel):
    idx: int
    ndviΔ: float = Field(..., alias="ndviΔ")
    soilΔ: float = Field(..., alias="soilΔ")
    waterΔ: float = Field(..., alias="waterΔ")

class TurnOut(BaseModel):
    deltas: Dict
    economy: Dict

class SummaryOut(BaseModel):
    score: Dict
    charts: Dict
    analysis_text: str
