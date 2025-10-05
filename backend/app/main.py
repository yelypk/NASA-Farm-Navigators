# backend/app/main.py
from contextlib import asynccontextmanager
import logging
from typing import Optional

from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from .logging_setup import setup_logging
setup_logging()

from .db import engine, get_db, ensure_db, list_tables
from .repo import dal  # <- локальный импорт

log = logging.getLogger("app.main")

@asynccontextmanager
async def lifespan(app: FastAPI):
    log.info("App startup: ensuring DB...")
    await ensure_db()
    try:
        tables = await list_tables()
        log.info("Public tables: %s", tables or "[] (empty)")
    except Exception:
        log.exception("Cannot list tables on startup")
    yield
    await engine.dispose()
    log.info("DB engine disposed, shutdown complete")

app = FastAPI(title="NASA Farm Navigators API", lifespan=lifespan)

@app.get("/healthz")
async def healthz():
    return {"ok": True}

@app.get("/readyz")
async def readyz(db: AsyncSession = Depends(get_db)):
    await db.execute(text("SELECT 1"))
    return {"db": "ok"}

@app.get("/debug/db-state")
async def debug_db_state():
    try:
        return {"tables": await list_tables()}
    except Exception as e:
        log.exception("debug/db-state failed")
        return {"error": str(e)}

# -------- Manifests/Catalog --------

@app.get("/manifests/crops")
async def get_crops(region: Optional[str] = None, db: AsyncSession = Depends(get_db)):
    """Вернёт список объектов из manifests_crops.json (колонка json)."""
    rows = await dal.get_crops(db, region=region)
    return rows  # list[dict]

@app.get("/manifests/infra")
async def get_infra(category: Optional[str] = None, db: AsyncSession = Depends(get_db)):
    """Вернёт список объектов infra (колонка json)."""
    rows = await dal.get_infra(db, category=category)
    return rows  # list[dict]

@app.get("/regions")
async def list_regions(db: AsyncSession = Depends(get_db)):
    return await dal.list_regions(db)

# -------- Game session --------

class NewGameRequest(BaseModel):
    region_name: str
    preset: str = "default"
    seed_rng: Optional[int] = None
    config_overrides: Optional[dict] = None

@app.post("/game/new")
async def new_game(req: NewGameRequest, db: AsyncSession = Depends(get_db)):
    # простой "effective config" из таблицы regions (+ overrides)
    region = await dal.get_region_by_name(db, req.region_name)
    if region is None:
        raise HTTPException(status_code=404, detail="Region not found")

    config = {
        "preset": req.preset,
        "grid": {"w": region["grid_w"], "h": region["grid_h"], "tile_m": region["tile_m"]},
        "meta": region["meta_json"] or {},
    }
    if req.config_overrides:
        # поверх добавляем overrides
        config.update(req.config_overrides)

    session_id = await dal.create_game_session(
        db,
        region_id=region["id"],
        preset=req.preset,
        config_json=config,
        seed_rng=req.seed_rng,
        manifests_sha=None,  # при желании вычислим позже
        config_sha=None,     # можно посчитать хеш json при необходимости
    )
    return {"session_id": session_id, "region_id": region["id"], "preset": req.preset}
