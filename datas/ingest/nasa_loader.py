from pathlib import Path
import numpy as np

class NasaLoader:
    def __init__(self, root: Path):
        self.root = root

    def load_timeseries(self, region_id: str, years: range):
        # In real life: open NetCDF/HDF/GeoTIFF, reproject, clip, etc.
        # Here: return random-but-stable arrays for reproducibility.
        rng = np.random.default_rng(42)
        data = {}
        for y in years:
            data[y] = {
                "ndvi": rng.random((100, 100)).astype(np.float32),
                "soil_moisture": rng.random((100, 100)).astype(np.float32),
                "precip": rng.random((100, 100)).astype(np.float32),
                "temp": rng.random((100, 100)).astype(np.float32),
                "wind": rng.random((100, 100)).astype(np.float32),
            }
        return data
