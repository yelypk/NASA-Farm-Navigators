from fastapi import FastAPI, HTTPException, APIRouter
from fastapi.responses import Response, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import logging

# ====== game imports ======
from .storage import store
from .models import NewGameRequest, PlanRequest
from .sim.engine import new_game_state, apply_plan_and_tick
from .sim.render import render_raster_png

# ====== EO (satellite layers) imports — optional fallback if package not added yet ======
_EO_AVAILABLE = True
_EO_IMPORT_ERROR_TEXT = ""
try:
    from .eo.sources import EOLayers, RegionStore, GridMeta
    from .eo.encode import to_grayscale_png
    from .eo.viz_presets import SCALES
except Exception as _e:
    _EO_AVAILABLE = False
    _EO_IMPORT_ERROR_TEXT = f"{type(_e).__name__}: {_e}"

app = FastAPI(title="Farm Navigators API")

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
# EO layers API (frontend consumes grayscale PNG + colors on client)
# --------------------------------------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parents[2]
DATA_ROOT = (REPO_ROOT / "backend" / "data").resolve()

def _region_store(region_id: str) -> "RegionStore":
    if not _EO_AVAILABLE:
        raise HTTPException(
            503,
            detail=f"EO stack not yet installed in backend (.eo/*). Import error: {_EO_IMPORT_ERROR_TEXT}"
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
            detail=f"EO stack not yet installed in backend (.eo/*). Import error: {_EO_IMPORT_ERROR_TEXT}"
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
    Shape assumptions follow GridMeta (default 200x200, 4 seasons * 20 years).
    """
    if not _EO_AVAILABLE:
        raise HTTPException(
            503,
            detail=f"EO stack not yet installed in backend (.eo/*). Import error: {_EO_IMPORT_ERROR_TEXT}"
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
# SPA / static
# --------------------------------------------------------------------------------------
STATIC_DIR = Path(__file__).resolve().parent / "static"   # prod: copy frontend build here
DIST_DIR   = REPO_ROOT / "frontend" / "dist"              # local: vite build output
FRONTEND_DIR = next((p for p in (STATIC_DIR, DIST_DIR) if (p / "index.html").exists()), None)

if FRONTEND_DIR:
    # ВАЖНО: монтируем весь dist на корень -> файлы типа /legend_ndvi.png и /assets/* отдаются корректно
    app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="spa")
else:
    logging.getLogger("app.main").warning(
        "No frontend build found at %s or %s", STATIC_DIR, DIST_DIR
    )

# --------------------------------------------------------------------------------------
# Debug endpoints (no route path collisions)
# --------------------------------------------------------------------------------------
_dbg = APIRouter()

@_dbg.get("/__debug_frontend", include_in_schema=False)
def dbg_frontend():
    return {
        "static_index": (STATIC_DIR / "index.html").exists(),
        "dist_index":   (DIST_DIR / "index.html").exists(),
        "static_dir": str(STATIC_DIR),
        "dist_dir":   str(DIST_DIR)
    }

@_dbg.get("/__debug/eo_status", include_in_schema=False)
def dbg_eo_status():
    return {
        "eo_available": _EO_AVAILABLE,
        "data_root": str(DATA_ROOT),
        "import_error": _EO_IMPORT_ERROR_TEXT or None
    }

app.include_router(_dbg)
# ========= /SPA serving =========
