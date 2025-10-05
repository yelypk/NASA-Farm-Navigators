# backend/app/repo/dal.py
from typing import Optional, List, Dict, Any
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import (
    ManifestCrop,
    ManifestInfrastructure,
    Region,
    Session as GameSession,
)

# ---- Manifests ----

async def get_crops(db: AsyncSession, region: Optional[str] = None) -> List[Dict[str, Any]]:
    """Вернёт список JSON объектов культур; если region задан — фильтруем по колонке ManifestCrop.region."""
    if region:
        stmt = select(ManifestCrop.json).where(ManifestCrop.region == region)
    else:
        stmt = select(ManifestCrop.json)
    res = await db.execute(stmt)
    return [row[0] for row in res.all()]

async def get_infra(db: AsyncSession, category: Optional[str] = None) -> List[Dict[str, Any]]:
    """Вернёт список JSON объектов инфраструктуры; можно фильтровать по category."""
    if category:
        stmt = select(ManifestInfrastructure.json).where(ManifestInfrastructure.category == category)
    else:
        stmt = select(ManifestInfrastructure.json)
    res = await db.execute(stmt)
    return [row[0] for row in res.all()]

# ---- Regions ----

async def list_regions(db: AsyncSession) -> List[Dict[str, Any]]:
    stmt = select(
        Region.id,
        Region.name,
        Region.grid_w,
        Region.grid_h,
        Region.tile_m,
        Region.meta_json,
    ).order_by(Region.name.asc())
    res = await db.execute(stmt)
    out = []
    for rid, name, gw, gh, tm, meta in res.all():
        out.append({"id": rid, "name": name, "grid_w": gw, "grid_h": gh, "tile_m": tm, "meta_json": meta})
    return out

async def get_region_by_name(db: AsyncSession, name: str) -> Optional[Dict[str, Any]]:
    stmt = select(
        Region.id,
        Region.name,
        Region.grid_w,
        Region.grid_h,
        Region.tile_m,
        Region.meta_json,
    ).where(Region.name == name)
    res = await db.execute(stmt)
    row = res.first()
    if not row:
        return None
    rid, name, gw, gh, tm, meta = row
    return {"id": rid, "name": name, "grid_w": gw, "grid_h": gh, "tile_m": tm, "meta_json": meta}

# ---- Sessions ----

async def create_game_session(
    db: AsyncSession,
    *,
    region_id: int,
    preset: str,
    config_json: dict,
    seed_rng: Optional[int],
    config_sha: Optional[str] = None,
    manifests_sha: Optional[str] = None,
) -> int:
    row = GameSession(
        region_id=region_id,
        preset=preset,
        config_json=config_json,
        config_sha=config_sha,
        manifests_sha=manifests_sha,
        seed_rng=seed_rng,
    )
    db.add(row)
    await db.commit()
    await db.refresh(row)
    return row.id
