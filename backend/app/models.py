from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Literal
import uuid, math

Season = Literal["spring","summer","autumn","winter"]

class PlanCell(BaseModel):
    crop: Optional[str] = None
    irrigation: Optional[bool] = None
    drainage: Optional[bool] = None

class PlanRequest(BaseModel):
    cells: Dict[str, PlanCell] = Field(default_factory=dict)

class NewGameRequest(BaseModel):
    region: Literal["california","amu_darya","sahel"]
    seed: Optional[int] = None

class CellPlan(BaseModel):
    crop: str = "fallow"
    irrigation: bool = False
    drainage: bool = False

class Cell(BaseModel):
    fertility: float = 0.6  # 0..1
    salinity: float = 0.2   # 0..1 (bad if high)
    moisture: float = 0.5   # 0..1
    ndvi: float = 0.25      # 0..1
    last_crop: str = "fallow"
    plan: CellPlan = Field(default_factory=CellPlan)

class Farm(BaseModel):
    size: int = 32  # 32x32 = 1km @ ~31m cell
    cells: List[Cell] = Field(default_factory=list)

    def __init__(self, **data):
        super().__init__(**data)
        if not self.cells:
            self.cells = [Cell() for _ in range(self.size*self.size)]

    def rasters(self, layer: str):
        import numpy as np
        n = self.size
        arr = np.zeros((n, n), dtype="float32")
        for i, c in enumerate(self.cells):
            y = i // n; x = i % n
            if layer == "ndvi":
                arr[y,x] = c.ndvi
            elif layer == "moisture":
                arr[y,x] = c.moisture
            elif layer == "salinity":
                arr[y,x] = c.salinity
            elif layer == "fertility":
                arr[y,x] = c.fertility
            else:
                arr[y,x] = 0.0
        return arr.clip(0.0, 1.0)

class Finance(BaseModel):
    cash: float = 10000.0
    loan: float = 0.0
    score_economy: float = 0.0
    score_sustain: float = 0.0
    score_risk: float = 0.0
    score_efficiency: float = 0.0

class Climate(BaseModel):
    # Simplified seasonal drivers per region
    seasonal_rain: Dict[Season, float]
    seasonal_temp: Dict[Season, float]
    # shocks loaded from events
    shock_rain: float = 1.0
    shock_temp: float = 1.0

class Region(BaseModel):
    code: str
    display_name: str
    climate: Climate

class GameState(BaseModel):
    id: str
    region: Region
    farm: Farm
    finance: Finance = Field(default_factory=Finance)
    year: int = 2014
    season: Season = "spring"
    turn: int = 0  # total seasons played

    def public(self):
        return {
            "id": self.id,
            "year": self.year,
            "season": self.season,
            "turn": self.turn,
            "region": self.region.dict(),
            "finance": self.finance.dict(),
            "kpis": {
                "avg_ndvi": self.avg_ndvi(),
                "avg_moisture": self.avg_moisture(),
                "avg_salinity": self.avg_salinity(),
                "avg_fertility": self.avg_fertility(),
            }
        }

    def advance_season(self):
        order = ["spring","summer","autumn","winter"]
        i = order.index(self.season)
        nxt = order[(i+1)%4]
        self.season = nxt
        if nxt == "spring":
            self.year += 1

    def avg_ndvi(self): 
        return sum(c.ndvi for c in self.farm.cells)/len(self.farm.cells)
    def avg_moisture(self): 
        return sum(c.moisture for c in self.farm.cells)/len(self.farm.cells)
    def avg_salinity(self): 
        return sum(c.salinity for c in self.farm.cells)/len(self.farm.cells)
    def avg_fertility(self): 
        return sum(c.fertility for c in self.farm.cells)/len(self.farm.cells)
