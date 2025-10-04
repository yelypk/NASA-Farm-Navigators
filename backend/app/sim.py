import numpy as np
from typing import Dict, Any

def climate_drivers(S, t: int) -> Dict[str, float]:
    return {
        "rain": float(np.nanmean(S["region"]["rain_anom"][t])),
        "dry":  float(np.nanmean(S["region"]["soil_dry"][t])),
        "temp": float(np.nanmean(S["region"]["temp_anom"][t])),
    }

def step_farm(st, S, t: int):
    farm = st["farm"]
    plan = farm.get("plan") or {"crops":[["fallow"]*40 for _ in range(40)],
                                "irrigation_rate":0.0,
                                "practices":{}}
    rain = climate_drivers(S,t)["rain"]
    dry  = climate_drivers(S,t)["dry"]
    temp = climate_drivers(S,t)["temp"]

    irr  = float(plan.get("irrigation_rate", 0.0))
    cover = plan.get("practices",{}).get("cover_crop", 0.0)
    mulch = plan.get("practices",{}).get("mulch", 0.0)

    recharge = max(0.0, 0.03 * (1.0 + rain))
    water_use = 0.06 * irr
    farm["aquifer"] = float(np.clip(farm["aquifer"] + recharge - water_use, 0.0, 2.0))

    stress = np.clip(dry - 0.5*irr - 0.05*cover - 0.05*mulch + 0.2*max(0.0,temp), 0.0, 1.0)

    d_soil =  +0.02*cover + 0.02*mulch - 0.03*stress - 0.02*max(0.0, irr-0.7)
    farm["soil"] = np.clip(farm["soil"] + d_soil, 0.0, 1.0)

    soil_mean = float(np.mean(farm["soil"]))
    ndvi_sim  = float(np.clip(0.30 + 0.5*(1.0-stress) + 0.20*soil_mean, 0.0, 1.0))

    revenue = 12_000.0 * ndvi_sim
    costs   =  2_500.0 + 6_000.0 * irr + 1_000.0*(cover>0) + 1_000.0*(mulch>0)
    farm["cash"] = float(farm["cash"] + revenue - costs)

    farm["alpha"] = float(np.clip(farm["alpha"] + 0.02*cover + 0.02*mulch - 0.01*(irr>0.8), 0.0, 0.6))

    ndvi_hist = S["region"]["ndvi_hist"][t]
    arr_prime = st["region_prime"]["ndvi_prime"]
    if not arr_prime.any():
        st["region_prime"]["ndvi_prime"][:] = S["region"]["ndvi_hist"]

    cx, cy = S["meta"]["region_grid"]["farm_center_xy"]
    patch_hist = ndvi_hist[cy-1:cy+2, cx-1:cx+2]
    patch_sim  = np.full_like(patch_hist, ndvi_sim, dtype=np.float32)
    alpha = farm["alpha"]
    patch_prime = (1.0 - alpha)*patch_hist + alpha*patch_sim
    st["region_prime"]["ndvi_prime"][t, cy-1:cy+2, cx-1:cx+2] = patch_prime

    return {
        "ndvi_sim": ndvi_sim,
        "soil_mean": soil_mean,
        "aquifer": farm["aquifer"],
        "cash": farm["cash"]
    }
