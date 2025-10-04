from pathlib import Path
import json
from ingest.nasa_loader import NasaLoader
from .gridify import gridify_and_normalize

# Generates toy tiles for region "california" across 2010..2016
OUT = Path(__file__).resolve().parents[1] / "out" / "tiles" / "california"

YEARS = range(2010, 2017)
LAYERS = ["ndvi", "soil_moisture", "precip", "temp", "wind"]

if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    loader = NasaLoader(Path("."))
    ts = loader.load_timeseries("california", YEARS)
    for y in YEARS:
        norm = gridify_and_normalize(ts[y])
        payload = {k: norm[k].ravel().tolist() for k in LAYERS}
        payload.update({"w": 100, "h": 100, "year": y, "region_id": "california"})
        (OUT / f"{y}.json").write_text(json.dumps(payload))
    # scenario metadata
    meta = {
        "id": "california",
        "name": "California (Toy)",
        "years": list(YEARS),
        "grid": {"w": 100, "h": 100},
        "layers": LAYERS,
    }
    meta_path = Path(__file__).resolve().parents[1] / "scenarios" / "california"
    meta_path.mkdir(parents=True, exist_ok=True)
    (meta_path / "metadata.json").write_text(json.dumps(meta, indent=2))
    print(f"Wrote tiles to {OUT}")
