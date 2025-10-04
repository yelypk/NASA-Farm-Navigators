import json, os
from typing import Dict, Any
import numpy as np

DATA_ROOT = os.getenv("DATA_ROOT", "data")

def list_scenarios():
    return [d for d in os.listdir(DATA_ROOT) if os.path.isdir(os.path.join(DATA_ROOT,d))]

def load_scenario(name: str) -> Dict[str, Any]:
    base = f"{DATA_ROOT}/{name}"
    with open(f"{base}/meta.json","r",encoding="utf-8") as f:
        meta = json.load(f)
    region = {
        "ndvi_hist": np.load(f"{base}/region/ndvi_hist.npy"),
        "rain_anom": np.load(f"{base}/region/rain_anom.npy"),
        "soil_dry":  np.load(f"{base}/region/soil_dry.npy"),
        "temp_anom": np.load(f"{base}/region/temp_anom.npy"),
        "landuse_png": f"{base}/region/landuse.png",
    }
    farm = {
        "soil": np.load(f"{base}/farm/soil_health.npy").astype(np.float32),
        "mask_fields_png": f"{base}/farm/mask_fields.png",
        "base_cover_png": f"{base}/farm/base_cover.png",
    }
    return {"meta": meta, "region": region, "farm": farm}

def new_save_struct(scenario: str, S: Dict[str, Any], seed: int = 42) -> Dict[str, Any]:
    rng = np.random.default_rng(seed)
    return {
        "scenario": scenario,
        "t": 0,
        "rng": rng,
        "region_prime": {
            "ndvi_prime": np.zeros_like(S["region"]["ndvi_hist"], dtype=np.float32)
        },
        "farm": {
            "soil": S["farm"]["soil"].copy(),
            "aquifer": 1.0,
            "cash": 100_000.0,
            "alpha": 0.20,
            "plan": None
        },
        "meta": S["meta"],
    }
