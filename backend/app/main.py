from fastapi import FastAPI, HTTPException, APIRouter
from fastapi.responses import Response, JSONResponse    
from .storage import store
from .models import NewGameRequest, PlanRequest
from .sim.engine import new_game_state, apply_plan_and_tick
from .sim.render import render_raster_png
from pathlib import Path
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import logging

app = FastAPI(title="Farm Navigators API")

@app.get("/healthz")
def healthz():
    return {"ok": True}

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
        except:
            continue
        if 0 <= idx < len(gs.farm.cells):
            gs.farm.cells[idx].plan.crop = plan.crop or gs.farm.cells[idx].plan.crop
            gs.farm.cells[idx].plan.irrigation = plan.irrigation if plan.irrigation is not None else gs.farm.cells[idx].plan.irrigation
            gs.farm.cells[idx].plan.drainage = plan.drainage if plan.drainage is not None else gs.farm.cells[idx].plan.drainage
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

REPO_ROOT = Path(__file__).resolve().parents[2]
STATIC_DIR = Path(__file__).resolve().parent / "static"   # прод: сюда копируем dist
DIST_DIR   = REPO_ROOT / "frontend" / "dist"              # локалка: vite build

FRONTEND_DIR = next((p for p in (STATIC_DIR, DIST_DIR) if (p / "index.html").exists()), None)

if FRONTEND_DIR:
    # ВАЖНО: монтируем весь dist на корень -> файлы типа /legend_ndvi.png и /assets/* отдаются корректно
    app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="spa")
else:
    logging.getLogger("app.main").warning(
        "No frontend build found at %s or %s", STATIC_DIR, DIST_DIR
    )

# оставляем хелс/диагностику
_dbg = APIRouter()

@_dbg.get("/healthz", include_in_schema=False)
def healthz(): return {"status": "ok"}

@_dbg.get("/__debug_frontend", include_in_schema=False)
def dbg():
    return {
        "static_index": (STATIC_DIR / "index.html").exists(),
        "dist_index":   (DIST_DIR / "index.html").exists(),
        "static_dir": str(STATIC_DIR),
        "dist_dir":   str(DIST_DIR)
    }

app.include_router(_dbg)
# ========= /SPA serving =========