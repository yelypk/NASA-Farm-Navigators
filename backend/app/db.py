import os
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy import text

def _normalize(url: str) -> str:
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql+psycopg://", 1)
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+psycopg://", 1)
    return url

raw = os.getenv("DATABASE_URL")
if not raw:
    raise RuntimeError("DATABASE_URL is not set")
DATABASE_URL = _normalize(raw)

engine = create_async_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False, autoflush=False)

async def get_db():
    async with SessionLocal() as s:
        yield s

# опционально: явная проверка соединения
async def ensure_db():
    async with engine.connect() as conn:
        await conn.execute(text("SELECT 1"))
