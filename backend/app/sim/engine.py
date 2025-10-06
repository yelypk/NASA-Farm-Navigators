import uuid, random
from typing import Dict
import numpy as np
from ..models import GameState, Region, Climate, Farm, Finance
from .manifests import CROPS, REGIONS
from .events import apply_event_shocks

def new_game_state(region_code: str, seed: int | None) -> GameState:
    rng = random.Random(seed or 1337)
    reg = REGIONS[region_code]
    region = Region(
        code = region_code,
        display_name = reg["display"],
        climate = Climate(
            seasonal_rain = reg["seasonal_rain"],
            seasonal_temp = reg["seasonal_temp"],
        )
    )
    farm = Farm(size=32)
    # Init some spatial variation
    n = farm.size
    for i, c in enumerate(farm.cells):
        y = i // n; x = i % n
        c.moisture = 0.4 + 0.1*np.sin(x/7) + 0.05*np.cos(y/5)
        c.salinity = 0.2 + 0.1*np.sin(x/13) * np.cos(y/11)
        c.fertility = 0.55 + 0.1*np.cos(x/9) * np.cos(y/9)
        c.ndvi = max(0.1, c.fertility - c.salinity*0.25)
    gs = GameState(
        id=str(uuid.uuid4())[:8],
        region=region,
        farm=farm,
        finance=Finance(),
    )
    return gs

def season_index(season: str) -> int:
    return ["spring","summer","autumn","winter"].index(season)

def apply_plan_and_tick(gs: GameState) -> None:
    # 1) event shocks (droughts/floods/heatwaves) -> modifies climate shock multipliers this season
    apply_event_shocks(gs)
    rain = gs.region.climate.seasonal_rain[gs.season] * gs.region.climate.shock_rain
    temp = gs.region.climate.seasonal_temp[gs.season] * gs.region.climate.shock_temp

    # 2) per-cell water balance & salinity
    n = gs.farm.size
    for c in gs.farm.cells:
        crop = CROPS.get(c.plan.crop, CROPS["fallow"])
        water_need = crop["water"]
        # irrigation and drainage toggles
        irrigation_boost = 0.25 if c.plan.irrigation else 0.0
        drainage_relief = 0.1 if c.plan.drainage else 0.0

        # moisture update
        et = 0.25 + 0.35*temp  # evapotranspiration driver
        c.moisture = c.moisture + rain + irrigation_boost - et
        c.moisture = max(0.0, min(1.0, c.moisture))

        # salinity accumulates if high irrigation without drainage; decreases with drainage + rainfall
        if c.plan.irrigation and not c.plan.drainage:
            c.salinity += 0.05*(0.5 + water_need)
        c.salinity -= 0.04*(rain + (0.4 if c.plan.drainage else 0.0))
        c.salinity = max(0.0, min(1.0, c.salinity))

        # fertility: small gain with legumes/alfalfa/cover; small loss with exhaustive crops
        if c.plan.crop in ("alfalfa",):
            c.fertility += 0.02
        elif c.plan.crop in ("wheat","maize","cotton","millet"):
            c.fertility -= 0.01
        else:
            c.fertility += 0.005  # fallow/cover
        c.fertility = max(0.2, min(1.0, c.fertility))

        # NDVI response: peak by crop, damped by stress penalties
        stress_water = max(0.0, water_need - c.moisture)  # unmet demand
        # salinity stress: ratio vs crop tolerance
        tol = max(1e-3, CROPS.get(c.plan.crop, CROPS["fallow"])["salt"])
        stress_salt = max(0.0, (c.salinity - tol*0.5))
        growth = crop["ndvi_peak"] * (1.0 - 0.6*stress_water - 0.5*stress_salt) * (0.8 + 0.4*c.fertility)
        growth = max(0.05, min(0.95, growth))
        # seasonal phenology: lower in winter, highest in summer
        phen = {"spring":0.9,"summer":1.0,"autumn":0.8,"winter":0.5}[gs.season]
        target_ndvi = growth * phen
        # relax towards target
        c.ndvi = 0.6*c.ndvi + 0.4*target_ndvi

        # update last_crop at the end of season
        c.last_crop = c.plan.crop or c.last_crop

    # 3) finances (extremely simplified)
    income = 0.0; cost = 0.0
    for c in gs.farm.cells:
        crop = CROPS.get(c.plan.crop, CROPS["fallow"])
        # proxy yield by ndvi and fertility
        yield_factor = c.ndvi * (0.5 + 0.5*c.fertility)
        y = crop["yield"] * yield_factor
        income += y * crop["price"] / 100.0  # scaling for cell fraction
        if c.plan.irrigation: cost += 1.2
        if c.plan.drainage: cost += 0.8
    gs.finance.cash += income - cost

    # 4) scoring snapshots
    gs.finance.score_economy = 0.7*gs.finance.score_economy + 0.3*(income - cost)
    # sustainability: high fertility, low salinity, moderate moisture
    sustain = (1.2*avg_attr(gs.farm.cells, "fertility") - 0.8*avg_attr(gs.farm.cells, "salinity")
               - 0.2*abs(avg_attr(gs.farm.cells,"moisture")-0.6))
    gs.finance.score_sustain = 0.7*gs.finance.score_sustain + 0.3*sustain
    # risk: variance of moisture/salinity (lower is better)
    risk = - (np.std([c.moisture for c in gs.farm.cells]) + np.std([c.salinity for c in gs.farm.cells]))
    gs.finance.score_risk = 0.7*gs.finance.score_risk + 0.3*risk
    # efficiency: NDVI per unit cost
    eff = (avg_attr(gs.farm.cells,"ndvi")+1e-4)/(1.0+cost/100.0)
    gs.finance.score_efficiency = 0.7*gs.finance.score_efficiency + 0.3*eff

    # 5) advance time
    gs.turn += 1
    gs.advance_season()

def avg_attr(cells, k):
    return float(sum(getattr(c,k) for c in cells)/len(cells))
