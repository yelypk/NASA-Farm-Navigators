import random
from ..models import GameState

# Very small illustrative event system. Region- and season-specific modifiers.
def apply_event_shocks(gs: GameState) -> None:
    # reset shocks
    gs.region.climate.shock_rain = 1.0
    gs.region.climate.shock_temp = 1.0

    r = random.random()
    if gs.region.code == "california" and gs.season in ("spring","summer"):
        # occasional drought
        if r < 0.18:
            gs.region.climate.shock_rain = 0.55
            gs.region.climate.shock_temp = 1.1
    if gs.region.code == "amu_darya" and gs.season in ("summer","autumn"):
        # salinity/hot wind episode -> effectively increases ET
        if r < 0.15:
            gs.region.climate.shock_temp = 1.15
    if gs.region.code == "sahel" and gs.season == "summer":
        # monsoon shift (either heavy rain or deficit)
        if r < 0.12:
            gs.region.climate.shock_rain = 1.35
        elif r < 0.24:
            gs.region.climate.shock_rain = 0.65
