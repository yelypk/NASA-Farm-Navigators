from dataclasses import dataclass
import numpy as np

@dataclass
class Coeffs:
    base_price: float = 200.0
    seed_cost: float = 40.0
    water_cost: float = 30.0
    soil_bonus: float = 0.2
    overdraft_penalty: float = 0.05

COEFFS = Coeffs()

def compute_yield(ndvi, precip, temp, soil, irrigation):
    y = 0.5*ndvi + 0.3*precip + 0.2*(1.0 - abs(temp - 0.5))
    y += 0.1*soil + 0.15*irrigation
    return np.clip(y, 0.0, 1.0)

def update_soil(soil, cover_crop=False, fertilizer=False):
    soil_next = soil + (0.05 if cover_crop else 0.0) + (0.07 if fertilizer else 0.0)
    return np.clip(soil_next - 0.02, 0.0, 1.0)

def economy(yield_arr, irrig_cells, n_cells):
    revenue = yield_arr.mean() * COEFFS.base_price * n_cells
    costs = COEFFS.seed_cost * n_cells + COEFFS.water_cost * len(irrig_cells)
    balance = revenue - costs
    return {"revenue": revenue, "costs": costs, "balance": balance}
