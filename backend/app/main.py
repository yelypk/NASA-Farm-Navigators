from fastapi import FastAPI, HTTPException, APIRouter
from fastapi.responses import Response
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import logging

# ====== game imports ======
from .storage import store
from .models import NewGameRequest, PlanRequest
from .sim.engine import new_game_state, apply_plan_and_tick
from .sim.render import render_raster_png

# ====== EO (satellite layers) optional import (даём внятную 503, если пакета ещё нет) ======
_EO_AVAILABLE = True
_EO_IMPORT_ERROR_TEXT = ""
try:
    from .eo.sources import EOLayers, RegionStore, GridMeta
    from .eo.encode import to_grayscale_png
    from .eo.viz_presets import SCALES
except Exception as _e:
    _EO_AVAILABLE = False
    _EO_IMPORT_ERROR_TEXT = f"{type(_e).__name__}: {_e}"

# --------------------------------------------------------------------------------------
# App
# --------------------------------------------------------------------------------------
app = FastAPI(title="Farm Navigators API")

# CORS — фронт может жить на другом домене Railway/локально
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # при желании сузить до своих доменов
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------------------------------------------------------------------------------------
# Paths for Railway (Root Directory = backend/)
#   __file__ = backend/app/main.py
#   BASE_DIR  = backend/
#   APP_DIR   = backend/app/
#   DATA_ROOT = backend/data/
#   STATIC_DIR (SPA) = backend/app/static/  (сюда копируем frontend/dist/*)
# --------------------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parents[1]
APP_DIR = BASE_DIR / "app"
DATA_ROOT = BASE_DIR / "data"

STATIC_DIR = APP_DIR / "static"  # прод-артефакты фронта
FRONTEND_DIR = STATIC_DIR if (STATIC_DIR / "index.html").exists() else None

if FRONTEND_DIR:
    app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="spa")
else:
    logging.getLogger("app.main").warning(
        "Frontend build not found at %s. Build Vite app and copy frontend/dist/* to backend/app/static/",
        STATIC_DIR,
    )

# --------------------------------------------------------------------------------------
# Health
# --------------------------------------------------------------------------------------
@app.get("/healthz")
def healthz():
    return {"ok": True}

# --------------------------------------------------------------------------------------
# Game API
# --------------------------------------------------------------------------------------
@app.post("/game/new")
def game_new(req: NewGameRequest):
    gs = new_game_state(req.region, req.seed)
    store[gs.id] = gs
    return gs.public()

@app.get("/game/{gid}/state")
def game_state(gid: str):
    gs = store.get(gid)
    if not gs:
        raise HTTPException(404, "game not found")
    return gs.public()

@app.post("/game/{gid}/plan")
def game_plan(gid: str, req: PlanRequest):
    gs = store.get(gid)
    if not gs:
        raise HTTPException(404, "game not found")
    # merge plan (simple overwrite per cell)
    for cell_id, plan in req.cells.items():
        try:
            idx = int(cell_id)
        except Exception:
            continue
        if 0 <= idx < len(gs.farm.cells):
            cur = gs.farm.cells[idx].plan
            cur.crop = plan.crop or cur.crop
            cur.irrigation = plan.irrigation if plan.irrigation is not None else cur.irrigation
            cur.drainage = plan.drainage if plan.drainage is not None else cur.drainage
    return {"ok": True}

@app.post("/game/{gid}/tick")
def game_tick(gid: str):
    gs = store.get(gid)
    if not gs:
        raise HTTPException(404, "game not found")
    apply_plan_and_tick(gs)
    return gs.public()

@app.get("/game/{gid}/raster")
def game_raster(gid: str, layer: str = "ndvi"):
    gs = store.get(gid)
    if not gs:
        raise HTTPException(404, "game not found")
    arr = gs.farm.rasters(layer)
    png = render_raster_png(arr)
    return Response(content=png, media_type="image/png")

# --------------------------------------------------------------------------------------
# EO layers API (frontend takes grayscale PNG and applies LUT client-side)
# --------------------------------------------------------------------------------------
def _region_store(region_id: str) -> "RegionStore":
    if not _EO_AVAILABLE:
        raise HTTPException(
            503,
            detail=f"EO stack not yet installed (.eo/*). Import error: {_EO_IMPORT_ERROR_TEXT}",
        )
    root = DATA_ROOT / region_id
    if not root.exists():
        raise HTTPException(status_code=404, detail=f"Region '{region_id}' not found at {root}")
    return RegionStore(region_id=region_id, root=root)

@app.get("/region/{region_id}/layer")
def get_region_layer(region_id: str, layer: str, season: int):
    """
    Returns a grayscale PNG (uint8) for a seasonal EO layer.
    layer: ndvi|rain|dry|temp
    season: 0..(years*4-1)
    """
    if not _EO_AVAILABLE:
        raise HTTPException(
            503,
            detail=f"EO stack not yet installed (.eo/*). Import error: {_EO_IMPORT_ERROR_TEXT}",
        )
    if layer not in SCALES:
        raise HTTPException(400, f"Unknown layer '{layer}'. Expected one of: {', '.join(SCALES.keys())}")

    store_ = _region_store(region_id)
    repo = EOLayers(store_)
    arr = repo.get_array(layer, season)
    scale = SCALES[layer]
    png = to_grayscale_png(arr, scale.vmin, scale.vmax)
    return Response(content=png, media_type="image/png")

@app.get("/region/{region_id}/timeseries")
def get_timeseries(region_id: str, layer: str, x: int, y: int):
    """
    Return per-cell seasonal time-series at grid coords (x,y).
    Follows GridMeta defaults (200x200, seasons=4*years).
    """
    if not _EO_AVAILABLE:
        raise HTTPException(
            503,
            detail=f"EO stack not yet installed (.eo/*). Import error: {_EO_IMPORT_ERROR_TEXT}",
        )
    if layer not in SCALES:
        raise HTTPException(400, f"Unknown layer '{layer}'. Expected one of: {', '.join(SCALES.keys())}")

    store_ = _region_store(region_id)
    repo = EOLayers(store_)
    grid = GridMeta()

    if not (0 <= x < grid.width and 0 <= y < grid.height):
        raise HTTPException(400, f"Point (x={x}, y={y}) out of grid bounds {grid.width}x{grid.height}")

    values = []
    for t in range(grid.seasons_total):
        values.append(float(repo.get_array(layer, t)[y, x]))
    return {"region": region_id, "layer": layer, "x": x, "y": y, "values": values}

# --------------------------------------------------------------------------------------
# Debug
# --------------------------------------------------------------------------------------
_dbg = APIRouter()

@_dbg.get("/__debug_frontend", include_in_schema=False)
def dbg_frontend():
    return {
        "static_index": (STATIC_DIR / "index.html").exists(),
        "static_dir": str(STATIC_DIR),
        "data_root": str(DATA_ROOT),
        "eo_available": _EO_AVAILABLE,
        "eo_import_error": _EO_IMPORT_ERROR_TEXT or None,
    }

app.include_router(_dbg)

