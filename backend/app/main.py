from fastapi import FastAPI, Response, Query, HTTPException
from typing import Dict
import numpy as np
from .models import NewGameIn, PlanIn, TickOut, FarmStateOut
from . import dataio
from .raster import arr_to_png_gray
from .sim import step_farm

app = FastAPI(title="NASA Farm Navigators API", version="0.1.0")
SAVES: Dict[str, dict] = {}

@app.get("/healthz")
def healthz(): return {"ok": True}

@app.get("/scenarios")
def scenarios():
    return dataio.list_scenarios()

@app.post("/game/new")
def game_new(payload: NewGameIn):
    S = dataio.load_scenario(payload.scenario)
    save_id = str(len(SAVES) + 1)
    SAVES[save_id] = dataio.new_save_struct(payload.scenario, S, payload.seed or 42)
    SAVES[save_id]["S"] = S
    return {"save_id": save_id, "t": 0}

@app.get("/farm/{save_id}/state", response_model=FarmStateOut)
def farm_state(save_id: str):
    st = SAVES.get(save_id)
    if not st: raise HTTPException(404, "save not found")
    farm = st["farm"]
    return FarmStateOut(
        t=st["t"],
        soil_mean=float(np.mean(farm["soil"])),
        aquifer=farm["aquifer"],
        cash=farm["cash"],
        alpha=farm["alpha"]
    )

@app.post("/farm/{save_id}/plan")
def set_plan(save_id: str, plan: PlanIn):
    st = SAVES.get(save_id)
    if not st: raise HTTPException(404, "save not found")
    st["farm"]["plan"] = plan.dict()
    return {"ok": True}

@app.post("/tick/{save_id}", response_model=TickOut)
def tick(save_id: str):
    st = SAVES.get(save_id)
    if not st: raise HTTPException(404, "save not found")
    S  = st["S"]; t = st["t"]
    T  = S["region"]["ndvi_hist"].shape[0]
    if t >= T: raise HTTPException(400, "end of timeline")
    out = step_farm(st, S, t)
    st["t"] = t + 1
    return TickOut(
        t_next=st["t"],
        ndvi_sim=out["ndvi_sim"],
        soil_mean=out["soil_mean"],
        aquifer=out["aquifer"],
        cash=out["cash"]
    )

@app.get("/region/{save_id}/layer")
def region_layer(save_id: str,
                 season: int = Query(0, ge=0),
                 layer: str = Query("ndvi")):
    st = SAVES.get(save_id)
    if not st: raise HTTPException(404, "save not found")
    S = st["S"]
    if season >= S["region"]["ndvi_hist"].shape[0]:
        raise HTTPException(400, "season out of range")

    if layer == "ndvi":
        base = S["region"]["ndvi_hist"][season]
        prime = st["region_prime"]["ndvi_prime"][season]
        arr = np.where(prime == 0, base, prime)
        png = arr_to_png_gray(arr, out_size=(512,512))
        return Response(content=png, media_type="image/png")
    elif layer == "rain":
        png = arr_to_png_gray(S["region"]["rain_anom"][season], out_size=(512,512))
        return Response(content=png, media_type="image/png")
    elif layer == "soil":
        arr = 1.0 - S["region"]["soil_dry"][season]
        png = arr_to_png_gray(arr, out_size=(512,512))
        return Response(content=png, media_type="image/png")
    elif layer == "temp":
        png = arr_to_png_gray(S["region"]["temp_anom"][season], out_size=(512,512))
        return Response(content=png, media_type="image/png")
    elif layer == "landuse":
        with open(S["region"]["landuse_png"], "rb") as f:
            return Response(content=f.read(), media_type="image/png")
    else:
        raise HTTPException(400, "unknown layer")

@app.get("/farm/{save_id}/raster")
def farm_raster(save_id: str, season: int = Query(0, ge=0),
                layer: str = Query("soil")):
    st = SAVES.get(save_id)
    if not st: raise HTTPException(404, "save not found")
    if layer == "soil":
        arr = st["farm"]["soil"]
        png = arr_to_png_gray(arr, out_size=(512,512))
        return Response(content=png, media_type="image/png")
    elif layer == "ndvi_sim":
        ndvi = np.clip(0.3 + 0.5*(1.0-0.5) + 0.2*float(np.mean(st["farm"]["soil"])), 0, 1)
        import numpy as np
        arr = np.full((40,40), float(ndvi), dtype=np.float32)
        png = arr_to_png_gray(arr, out_size=(512,512))
        return Response(content=png, media_type="image/png")
    else:
        raise HTTPException(400, "unknown layer")
