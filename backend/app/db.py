# backend/app/db.py
import os
import json
import logging
from pathlib import Path
from typing import AsyncGenerator, Iterable

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

# ---------------------------------------------------------------------
# ЛОГИ
# ---------------------------------------------------------------------
log = logging.getLogger("app.db")
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO").upper(),
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)

# ---------------------------------------------------------------------
# ПОДКЛЮЧЕНИЕ
# ---------------------------------------------------------------------
def _normalize(url: str) -> str:
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql+psycopg://", 1)
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+psycopg://", 1)
    return url

def _mask_dsn(url: str) -> str:
    try:
        head, tail = url.split("://", 1)
        if "@" in tail:
            creds, host = tail.split("@", 1)
            user = creds.split(":", 1)[0]
            tail = f"{user}:***@{host}"
        return f"{head}://{tail}"
    except Exception:
        return "<cannot-mask>"

raw = os.getenv("DATABASE_URL") or ""
if not raw:
    raise RuntimeError("DATABASE_URL is not set")
DATABASE_URL = _normalize(raw)
ECHO = os.getenv("SQLALCHEMY_ECHO", "0") == "1"

log.info("db.py loaded, DATABASE_URL=%s, echo=%s", _mask_dsn(DATABASE_URL), ECHO)

engine = create_async_engine(DATABASE_URL, pool_pre_ping=True, echo=ECHO)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False, autoflush=False)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as s:
        yield s

# ---------------------------------------------------------------------
# DDL (БЕЗ ALEMBIC)
# ---------------------------------------------------------------------
DDL_TYPES = """
DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'fin_kind') THEN
    CREATE TYPE fin_kind AS ENUM ('loan','subsidy','insurance','payment','penalty');
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'event_kind') THEN
    CREATE TYPE event_kind AS ENUM ('historical','procedural');
  END IF;
END$$;
"""

DDL_SCHEMA = """
CREATE TABLE IF NOT EXISTS manifests_infrastructure (
  id  SERIAL PRIMARY KEY,
  key VARCHAR(64) UNIQUE NOT NULL,
  display_name VARCHAR(128),
  category VARCHAR(64) NOT NULL,
  regions TEXT[],
  sustainable BOOLEAN NOT NULL DEFAULT FALSE,
  capex_usd_per_ha DOUBLE PRECISION,
  opex_usd_per_ha_per_season DOUBLE PRECISION,
  labor_hours_per_ha_per_season DOUBLE PRECISION,
  energy_kwh_per_ha_per_season DOUBLE PRECISION,
  area_mode VARCHAR(32),
  effects JSONB,
  json JSONB NOT NULL,
  calibration_needed BOOLEAN,
  notes TEXT,
  version VARCHAR(32),
  updated_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS manifests_crops (
  id  SERIAL PRIMARY KEY,
  key VARCHAR(64) UNIQUE NOT NULL,
  display_name VARCHAR(128),
  region VARCHAR(64) NOT NULL,
  growth_length_seasons INT,
  base_yield_kg_per_ha DOUBLE PRECISION,
  water_req_mm_total DOUBLE PRECISION,
  salinity_tolerance DOUBLE PRECISION,
  heat_tolerance DOUBLE PRECISION,
  price_usd_per_ton_baseline DOUBLE PRECISION,
  ndvi_profile JSONB,
  soil_effects JSONB,
  pest_pressure_mod DOUBLE PRECISION,
  calibration_needed BOOLEAN,
  json JSONB NOT NULL,
  version VARCHAR(32),
  updated_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS regions (
  id SERIAL PRIMARY KEY,
  name VARCHAR(128) UNIQUE NOT NULL,
  bbox_json JSONB,
  grid_w INTEGER NOT NULL DEFAULT 200,
  grid_h INTEGER NOT NULL DEFAULT 200,
  tile_m INTEGER NOT NULL DEFAULT 250,
  meta_json JSONB
);

CREATE TABLE IF NOT EXISTS region_allowed_crops (
  region_id INTEGER NOT NULL REFERENCES regions(id) ON DELETE CASCADE,
  crop_id   INTEGER NOT NULL REFERENCES manifests_crops(id) ON DELETE CASCADE,
  PRIMARY KEY (region_id, crop_id)
);

CREATE TABLE IF NOT EXISTS sessions (
  id SERIAL PRIMARY KEY,
  region_id INTEGER REFERENCES regions(id),
  preset VARCHAR(32) NOT NULL DEFAULT 'default',
  config_json JSONB NOT NULL DEFAULT '{}'::jsonb,
  config_sha VARCHAR(64),
  manifests_sha VARCHAR(64),
  started_at TIMESTAMPTZ DEFAULT now(),
  finished_at TIMESTAMPTZ,
  seed_rng INTEGER
);

CREATE TABLE IF NOT EXISTS fields (
  id SERIAL PRIMARY KEY,
  session_id INTEGER NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
  x INTEGER NOT NULL,
  y INTEGER NOT NULL,
  state JSONB,
  fertility DOUBLE PRECISION NOT NULL DEFAULT 50,
  salinity DOUBLE PRECISION NOT NULL DEFAULT 10,
  moisture DOUBLE PRECISION NOT NULL DEFAULT 50,
  ndvi DOUBLE PRECISION NOT NULL DEFAULT 0.2,
  protection INTEGER NOT NULL DEFAULT 0,
  CONSTRAINT uq_field_cell UNIQUE (session_id, x, y)
);

CREATE TABLE IF NOT EXISTS infra_placements (
  id SERIAL PRIMARY KEY,
  session_id INTEGER NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
  infra_id   INTEGER NOT NULL REFERENCES manifests_infrastructure(id),
  area_mode  VARCHAR(32) NOT NULL,
  tiles      INTEGER[],
  payload    JSONB,
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS plantings (
  id SERIAL PRIMARY KEY,
  session_id INTEGER NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
  crop_id INTEGER NOT NULL REFERENCES manifests_crops(id),
  field_id INTEGER NOT NULL REFERENCES fields(id) ON DELETE CASCADE,
  season_start INTEGER NOT NULL,
  status VARCHAR(32) NOT NULL DEFAULT 'growing'
);

CREATE TABLE IF NOT EXISTS livestock (
  id SERIAL PRIMARY KEY,
  session_id INTEGER NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
  kind VARCHAR(32) NOT NULL,
  headcount INTEGER NOT NULL DEFAULT 0,
  paddock_tiles INTEGER[],
  params JSONB
);

CREATE TABLE IF NOT EXISTS finances (
  id SERIAL PRIMARY KEY,
  session_id INTEGER NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
  kind fin_kind NOT NULL,
  amount DOUBLE PRECISION NOT NULL,
  season INTEGER NOT NULL,
  note VARCHAR(256)
);

CREATE TABLE IF NOT EXISTS events (
  id SERIAL PRIMARY KEY,
  session_id INTEGER NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
  kind event_kind NOT NULL,
  code VARCHAR(64) NOT NULL,
  payload JSONB,
  season INTEGER NOT NULL,
  resolved BOOLEAN NOT NULL DEFAULT FALSE,
  choice VARCHAR(32)
);

CREATE TABLE IF NOT EXISTS telemetry (
  id SERIAL PRIMARY KEY,
  session_id INTEGER NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
  season INTEGER NOT NULL,
  kpi JSONB NOT NULL
);
"""

DDL_INDEXES = """
CREATE INDEX IF NOT EXISTS idx_crops_region             ON manifests_crops(region);
CREATE INDEX IF NOT EXISTS idx_sessions_region          ON sessions(region_id);
CREATE INDEX IF NOT EXISTS idx_fields_session           ON fields(session_id);
CREATE INDEX IF NOT EXISTS idx_placements_session       ON infra_placements(session_id);
CREATE INDEX IF NOT EXISTS idx_plantings_session        ON plantings(session_id);
CREATE INDEX IF NOT EXISTS idx_finances_session_season  ON finances(session_id, season);
CREATE INDEX IF NOT EXISTS idx_events_session_season    ON events(session_id, season);
CREATE INDEX IF NOT EXISTS idx_telemetry_session_season ON telemetry(session_id, season);
CREATE INDEX IF NOT EXISTS idx_infra_category           ON manifests_infrastructure(category);
"""

async def create_schema() -> None:
    async with engine.begin() as conn:
        log.info("Creating types…")
        await conn.execute(text(DDL_TYPES))
        log.info("Creating tables…")
        await conn.execute(text(DDL_SCHEMA))
        log.info("Creating indexes…")
        await conn.execute(text(DDL_INDEXES))
    log.info("Schema: OK")

# ---------------------------------------------------------------------
# ЗАГРУЗКА МАНИФЕСТОВ (conf/*.json)
# ---------------------------------------------------------------------
def _project_root() -> Path:
    # backend/app/db.py -> parents[2] = корень репо
    return Path(__file__).resolve().parents[2]

def _find_file(candidate_paths: Iterable[Path]) -> Path:
    for p in candidate_paths:
        if p.exists():
            return p
    raise FileNotFoundError("File not found in: " + ", ".join(str(p) for p in candidate_paths))

def _load_json(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8-sig") as f:
        return json.load(f)

async def load_manifests_from_conf() -> None:
    root = _project_root()
    # основная локация: <repo_root>/conf/*.json
    crop_path = root / "conf" / "crops_manifest.json"
    infra_path = root / "conf" / "infrastructure_manifest.json"
    # запасные локации на случай, если сервис собирается из backend/
    candidates_crops = [
        crop_path,
        Path.cwd() / "conf" / "crops_manifest.json",
        root / "backend" / "conf" / "crops_manifest.json",
        Path("/app/conf/crops_manifest.json"),
        Path("/mnt/data/crops_manifest.json"),  # локальный запуск через /mnt/data
    ]
    candidates_infra = [
        infra_path,
        Path.cwd() / "conf" / "infrastructure_manifest.json",
        root / "backend" / "conf" / "infrastructure_manifest.json",
        Path("/app/conf/infrastructure_manifest.json"),
        Path("/mnt/data/infrastructure_manifest.json"),
    ]

    crops_file = _find_file(candidates_crops)
    infra_file = _find_file(candidates_infra)

    crops = _load_json(crops_file)
    infra  = _load_json(infra_file)
    log.info("Loaded manifests: crops=%d, infra=%d", len(crops), len(infra))

    def _dumps(x) -> str:
        return json.dumps(x, ensure_ascii=False)

    crop_sql = text("""
        INSERT INTO manifests_crops (
            key, display_name, region, growth_length_seasons,
            base_yield_kg_per_ha, water_req_mm_total,
            salinity_tolerance, heat_tolerance,
            price_usd_per_ton_baseline,
            ndvi_profile, soil_effects, pest_pressure_mod,
            calibration_needed, json, version, updated_at
        )
        VALUES (
            :key, :display_name, :region, :growth_length_seasons,
            :base_yield_kg_per_ha, :water_req_mm_total,
            :salinity_tolerance, :heat_tolerance,
            :price_usd_per_ton_baseline,
            CAST(:ndvi_profile AS JSONB), CAST(:soil_effects AS JSONB), :pest_pressure_mod,
            :calibration_needed, CAST(:json AS JSONB), :version, now()
        )
        ON CONFLICT (key) DO UPDATE SET
            display_name = EXCLUDED.display_name,
            region = EXCLUDED.region,
            growth_length_seasons = EXCLUDED.growth_length_seasons,
            base_yield_kg_per_ha = EXCLUDED.base_yield_kg_per_ha,
            water_req_mm_total = EXCLUDED.water_req_mm_total,
            salinity_tolerance = EXCLUDED.salinity_tolerance,
            heat_tolerance = EXCLUDED.heat_tolerance,
            price_usd_per_ton_baseline = EXCLUDED.price_usd_per_ton_baseline,
            ndvi_profile = EXCLUDED.ndvi_profile,
            soil_effects = EXCLUDED.soil_effects,
            pest_pressure_mod = EXCLUDED.pest_pressure_mod,
            calibration_needed = EXCLUDED.calibration_needed,
            json = EXCLUDED.json,
            version = EXCLUDED.version,
            updated_at = now()
    """)

    infra_sql = text("""
        INSERT INTO manifests_infrastructure (
            key, display_name, category, regions, sustainable,
            capex_usd_per_ha, opex_usd_per_ha_per_season,
            labor_hours_per_ha_per_season, energy_kwh_per_ha_per_season,
            area_mode, effects, calibration_needed, notes, json, version, updated_at
        )
        VALUES (
            :key, :display_name, :category, :regions, :sustainable,
            :capex_usd_per_ha, :opex_usd_per_ha_per_season,
            :labor_hours_per_ha_per_season, :energy_kwh_per_ha_per_season,
            :area_mode, CAST(:effects AS JSONB), :calibration_needed, :notes,
            CAST(:json AS JSONB), :version, now()
        )
        ON CONFLICT (key) DO UPDATE SET
            display_name = EXCLUDED.display_name,
            category = EXCLUDED.category,
            regions = EXCLUDED.regions,
            sustainable = EXCLUDED.sustainable,
            capex_usd_per_ha = EXCLUDED.capex_usd_per_ha,
            opex_usd_per_ha_per_season = EXCLUDED.opex_usd_per_ha_per_season,
            labor_hours_per_ha_per_season = EXCLUDED.labor_hours_per_ha_per_season,
            energy_kwh_per_ha_per_season = EXCLUDED.energy_kwh_per_ha_per_season,
            area_mode = EXCLUDED.area_mode,
            effects = EXCLUDED.effects,
            calibration_needed = EXCLUDED.calibration_needed,
            notes = EXCLUDED.notes,
            json = EXCLUDED.json,
            version = EXCLUDED.version,
            updated_at = now()
    """)

    crop_rows = []
    for r in crops:
        crop_rows.append({
            "key": r.get("id"),
            "display_name": r.get("display_name"),
            "region": r.get("region"),
            "growth_length_seasons": r.get("growth_length_seasons"),
            "base_yield_kg_per_ha": r.get("base_yield_kg_per_ha"),
            "water_req_mm_total": r.get("water_req_mm_total"),
            "salinity_tolerance": r.get("salinity_tolerance"),
            "heat_tolerance": r.get("heat_tolerance"),
            "price_usd_per_ton_baseline": r.get("price_usd_per_ton_baseline"),
            "ndvi_profile": _dumps(r.get("ndvi_profile")),
            "soil_effects": _dumps(r.get("soil_effects")),
            "pest_pressure_mod": r.get("pest_pressure_mod"),
            "calibration_needed": r.get("calibration_needed"),
            "json": _dumps(r),
            "version": r.get("version") or "v1",
        })

    infra_rows = []
    for r in infra:
        infra_rows.append({
            "key": r.get("id"),
            "display_name": r.get("display_name"),
            "category": r.get("category"),
            "regions": r.get("regions"),
            "sustainable": r.get("sustainable", False),
            "capex_usd_per_ha": r.get("capex_usd_per_ha"),
            "opex_usd_per_ha_per_season": r.get("opex_usd_per_ha_per_season"),
            "labor_hours_per_ha_per_season": r.get("labor_hours_per_ha_per_season"),
            "energy_kwh_per_ha_per_season": r.get("energy_kwh_per_ha_per_season"),
            "area_mode": r.get("area_mode"),
            "effects": _dumps(r.get("effects")),
            "calibration_needed": r.get("calibration_needed"),
            "notes": r.get("notes"),
            "json": _dumps(r),
            "version": r.get("version") or "v1",
        })

    async with engine.begin() as conn:
        log.info("Upserting %d crops…", len(crop_rows))
        if crop_rows:
            await conn.execute(crop_sql, crop_rows)
        log.info("Upserting %d infrastructure items…", len(infra_rows))
        if infra_rows:
            await conn.execute(infra_sql, infra_rows)

    log.info("Manifests loaded: OK")

# ---------------------------------------------------------------------
# ДОПОЛНИТЕЛЬНО: регионы и связки
# ---------------------------------------------------------------------
CREATE_REGIONS_SQL = """
INSERT INTO regions(name)
SELECT DISTINCT region FROM manifests_crops
ON CONFLICT (name) DO NOTHING;
"""

CREATE_REGION_ALLOWED_SQL = """
INSERT INTO region_allowed_crops(region_id, crop_id)
SELECT r.id, c.id
FROM manifests_crops c
JOIN regions r ON r.name = c.region
ON CONFLICT DO NOTHING;
"""

async def ensure_regions_and_links() -> None:
    async with engine.begin() as conn:
        await conn.execute(text(CREATE_REGIONS_SQL))
        await conn.execute(text(CREATE_REGION_ALLOWED_SQL))
    log.info("Regions and region_allowed_crops: OK")

# ---------------------------------------------------------------------
# ПРОВЕРКИ/УТИЛИТЫ
# ---------------------------------------------------------------------
async def ensure_db() -> None:
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

# ---------------------------------------------------------------------
# MAIN: автоматический bootstrap при запуске как скрипт
# ---------------------------------------------------------------------
if __name__ == "__main__":
    import asyncio

    async def main():
        log.info("=== DB bootstrap started ===")
        log.info("Working dir: %s", Path.cwd())
        await ensure_db()
        await create_schema()
        await load_manifests_from_conf()
        await ensure_regions_and_links()
        tables = await list_tables()
        log.info("Public tables: %s", tables)
        log.info("=== DB bootstrap done ===")

    asyncio.run(main())
