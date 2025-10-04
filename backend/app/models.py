from pydantic import BaseModel, Field
from typing import List, Dict, Literal, Optional

LayerName = Literal["ndvi","rain","soil","temp","landuse"]

class NewGameIn(BaseModel):
    scenario: str
    seed: Optional[int] = 42

class PlanIn(BaseModel):
    crops: List[List[str]]  # 40x40 имена культур / "fallow" / "cover"
    irrigation_rate: float = Field(ge=0.0, le=1.0, default=0.0)
    practices: Dict[str, float] = Field(default_factory=dict)  # {"cover_crop":1, "mulch":1, "shelterbelts":2}

class TickOut(BaseModel):
    t_next: int
    ndvi_sim: float
    soil_mean: float
    aquifer: float
    cash: float

class FarmStateOut(BaseModel):
    t: int
    soil_mean: float
    aquifer: float
    cash: float
    alpha: float
