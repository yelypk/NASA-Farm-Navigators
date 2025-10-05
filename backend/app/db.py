import os
import logging
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy import text

log = logging.getLogger("app.db")

def _normalize(url: str) -> str:
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql+psycopg://", 1)
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+psycopg://", 1)
    return url

def _mask_dsn(url: str) -> str:
    # postgresql+psycopg://user:pass@host:port/db?...
    try:
        head, tail = url.split("://", 1)
        cre_host = tail.split("@", 1)
        if len(cre_host) == 2:
            creds, host = cre_host
            if ":" in creds:
                user = creds.split(":", 1)[0]
                creds = f"{user}:***"
            else:
                creds = "***"
            tail = f"{creds}@{host}"
        return f"{head}://{tail}"
    except Exception:
        return "<cannot-mask>"

raw = os.getenv("DATABASE_URL")
if not raw:
    raise RuntimeError("DATABASE_URL is not set")

DATABASE_URL = _normalize(raw)
ECHO = os.getenv("SQLALCHEMY_ECHO", "0") == "1"
log.info("Import db.py, DATABASE_URL=%s, SQLALCHEMY_ECHO=%s", _mask_dsn(DATABASE_URL), ECHO)

engine = create_async_engine(DATABASE_URL, pool_pre_ping=True, echo=ECHO)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False, autoflush=False)

async def get_db():
    async with SessionLocal() as s:
        yield s

async def ensure_db():
    log.info("DB ping...")  # будет видно в Railway Logs
    async with engine.connect() as conn:
        await conn.execute(text("SELECT 1"))
    log.info("DB ping OK")

async def list_tables() -> list[str]:
    sql = text("""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema='public'
        ORDER BY table_name
    """)
    async with engine.connect() as conn:
        res = await conn.execute(sql)
        return [r[0] for r in res.fetchall()]

