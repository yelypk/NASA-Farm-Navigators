import numpy as np
from .model import compute_yield, update_soil, economy

def apply_turn(layers: dict, decisions: dict):
    w, h = layers["w"], layers["h"]
    n = w*h
    ndvi = np.array(layers["ndvi"], dtype=float).reshape(h, w)
    precip = np.array(layers["precip"], dtype=float).reshape(h, w)
    temp = np.array(layers["temp"], dtype=float).reshape(h, w)
    soil = np.array(layers.get("soil_moisture", layers["ndvi"])).reshape(h, w)

    irrig = np.zeros((h, w))
    irrig_cells = decisions.get("water", {}).get("irrigate_cells", [])
    for idx in irrig_cells:
        y, x = divmod(idx, w)
        irrig[y, x] = 1.0

    yld = compute_yield(ndvi, precip, temp, soil, irrig)
    soil_next = update_soil(soil, cover_crop=decisions.get("soil", {}).get("cover_crop") == "yes",
                            fertilizer=decisions.get("soil", {}).get("fertilizer") == "yes")

    econ = economy(yld, irrig_cells, n)

    deltas = []
    changed = np.where(irrig.ravel() > 0.0)[0]
    for idx in changed:
        deltas.append({"idx": int(idx), "ndviΔ": 0.02, "soilΔ": 0.01, "waterΔ": -0.02})

    return {
        "deltas": {"cells": deltas},
        "economy": econ,
        "next": {
            "soil_moisture": soil_next.ravel().tolist(),
        }
    }
