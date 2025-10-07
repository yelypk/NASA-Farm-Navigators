from dataclasses import dataclass
from pathlib import Path
import numpy as np

@dataclass
class GridMeta:
    width: int = 200
    height: int = 200
    seasons_per_year: int = 4
    years: int = 20

    @property
    def seasons_total(self) -> int:
        return self.years * self.seasons_per_year

@dataclass
class RegionStore:
    region_id: str
    root: Path  # e.g. backend/data/CA_SanJoaquin_West

    def layer_npy(self, layer: str, season: int) -> Path:
        # convention: backend/data/<region>/layers/<layer>/t_<season>.npy
        return self.root / "layers" / layer / f"t_{season}.npy"

    def meta_json(self) -> Path:
        return self.root / "meta.json"

class EOLayers:
    """
    Thin repository over pre-агрегированными массивами сезонов:
    - ndvi:    float32 0..1
    - rain:    float32 мм (или аномалия в σ, если решили)
    - dry:     float32 0..1 (1-SMAP)
    - temp:    float32 аномалия в °C (или σ)
    """
    def __init__(self, store: RegionStore, grid: GridMeta = GridMeta()):
        self.store, self.grid = store, grid

    def get_array(self, layer: str, season: int) -> np.ndarray:
        p = self.store.layer_npy(layer, season)
        arr = np.load(p)  # shape (H,W)
        # sanity shape
        if arr.shape != (self.grid.height, self.grid.width):
            raise ValueError(f"Bad shape for {layer}@{season}: {arr.shape}")
        return arr
