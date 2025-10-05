from contextlib import asynccontextmanager
import logging
from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from .logging_setup import setup_logging
setup_logging()  # <== важно: настроить логирование самым первым

from .db import engine, get_db, ensure_db, list_tables  # noqa: E402 (после setup_logging)

log = logging.getLogger("app.main")

@asynccontextmanager
async def lifespan(app: FastAPI):
    log.info("App startup: ensuring DB...")
    await ensure_db()
    # на старте покажем, какие таблицы видит БД
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

# Временный отладочный эндпойнт
@app.get("/debug/db-state")
async def debug_db_state():
    try:
        return {"tables": await list_tables()}
    except Exception as e:
        log.exception("debug/db-state failed")
        return {"error": str(e)}








