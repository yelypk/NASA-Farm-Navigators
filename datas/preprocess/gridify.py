import numpy as np

def normalize_layer(arr: np.ndarray) -> np.ndarray:
    vmin, vmax = arr.min(), arr.max()
    if vmax - vmin < 1e-9:
        return np.zeros_like(arr, dtype=np.float32)
    return ((arr - vmin) / (vmax - vmin)).astype(np.float32)

def gridify_and_normalize(year_data: dict) -> dict:
    # Assume input already 100x100; just normalize
    return {k: normalize_layer(v) for k, v in year_data.items()}
