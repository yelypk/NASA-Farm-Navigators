from pathlib import Path
import json
from typing import Dict
import os

TILES_PATH = Path(os.getenv("TILES_PATH", "../dataproc/out/tiles")).resolve()

class TilesRepo:
    def __init__(self, tiles_path: Path | None = None):
        self.path = tiles_path or TILES_PATH

    def get_year(self, region_id: str, year: int) -> Dict:
        f = self.path / region_id / f"{year}.json"
        return json.loads(f.read_text())

    def get_region_meta(self, region_id: str) -> Dict:
        meta = (self.path.parent.parent / "scenarios" / region_id / "metadata.json")
        return json.loads(meta.read_text())

    def list_regions(self) -> list[Dict]:
        regions = []
        scen = self.path.parent.parent / "scenarios"
        for d in scen.iterdir():
            if (d / "metadata.json").exists():
                regions.append(json.loads((d / "metadata.json").read_text()))
        return regions
