from ..models import DeltaSeason

def run(state, plans) -> DeltaSeason:
    # Stub: produce minimal deltas, to be replaced by real sim
    deltas = DeltaSeason.parse_obj({
        "yield": [],
        "soil": {"health_delta": 0.0},
        "water": {"used_m3": 0, "aquifer_delta_m": 0.0},
        "pests": {"pressure": 0.0},
        "finance": {"revenue": 0, "opex": 0, "capex": 0}
    })
    return deltas