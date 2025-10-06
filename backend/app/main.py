from fastapi import FastAPI, HTTPException
from fastapi.responses import Response, JSONResponse
from .storage import store
from .models import NewGameRequest, PlanRequest
from .sim.engine import new_game_state, apply_plan_and_tick
from .sim.render import render_raster_png
from pathlib import Path
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

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

APP_DIR = Path(__file__).resolve().parent
ROOT_DIR = APP_DIR.parent  # корень репо
FRONTEND_DIST = ROOT_DIR / "frontend" / "dist"

if FRONTEND_DIST.exists():
    assets_dir = FRONTEND_DIST / "assets"
    if assets_dir.exists():
        # Vite кладёт статичные ассеты сюда (с хешами в именах)
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

    @app.get("/", include_in_schema=False)
    async def index():
        """Корневая страница SPA."""
        return FileResponse(FRONTEND_DIST / "index.html")

    @app.get("/{path_name:path}", include_in_schema=False)
    async def spa_fallback(path_name: str):
        """
        Любой не-API маршрут (например /game, /settings) возвращает index.html.
        Все API-роуты, объявленные выше, сработают раньше и не попадут сюда.
        """
        index_file = FRONTEND_DIST / "index.html"
        if index_file.exists():
            return FileResponse(index_file)
        raise HTTPException(
            status_code=404,
            detail="Frontend is not built. Run: npm --prefix frontend ci && npm --prefix frontend run build",
        )
else:
    import logging
    logging.getLogger("app.main").warning(
        "frontend/dist not found; '/' will be 404. Build the frontend before deploy."
    )
