from datetime import datetime
from sqlalchemy import (
    Integer, String, Float, Boolean, DateTime, ForeignKey, Enum, UniqueConstraint
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSONB, ARRAY

class Base(DeclarativeBase):
    pass

# -------- Маніфести --------
class ManifestInfrastructure(Base):
    __tablename__ = "manifests_infrastructure"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    key: Mapped[str] = mapped_column(String(64), unique=True, index=True)  # например "irrigation_drip"
    json: Mapped[dict] = mapped_column(JSONB)                               # оригинальный объект
    category: Mapped[str] = mapped_column(String(64))
    sustainable: Mapped[bool] = mapped_column(Boolean, default=False)
    regions: Mapped[list[str]] = mapped_column(ARRAY(String(64)))
    capex_usd_per_ha: Mapped[float | None] = mapped_column(Float, nullable=True)
    opex_usd_per_ha_per_season: Mapped[float | None] = mapped_column(Float, nullable=True)
    version: Mapped[str | None] = mapped_column(String(32), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class ManifestCrop(Base):
    __tablename__ = "manifests_crops"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    key: Mapped[str] = mapped_column(String(64), unique=True, index=True)  # например "almond"
    json: Mapped[dict] = mapped_column(JSONB)
    region: Mapped[str] = mapped_column(String(64), index=True)
    base_yield: Mapped[float | None] = mapped_column(Float, nullable=True)
    water_req: Mapped[float | None] = mapped_column(Float, nullable=True)
    price_usd_per_ton: Mapped[float | None] = mapped_column(Float, nullable=True)
    version: Mapped[str | None] = mapped_column(String(32), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

# -------- Регіони і дозволені культури --------
class Region(Base):
    __tablename__ = "regions"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    bbox_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    grid_w: Mapped[int] = mapped_column(Integer, default=200)
    grid_h: Mapped[int] = mapped_column(Integer, default=200)
    tile_m: Mapped[int] = mapped_column(Integer, default=250)
    meta_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

class RegionAllowedCrop(Base):
    __tablename__ = "region_allowed_crops"
    region_id: Mapped[int] = mapped_column(ForeignKey("regions.id"), primary_key=True)
    crop_id: Mapped[int] = mapped_column(ForeignKey("manifests_crops.id"), primary_key=True)

# -------- Ігрова сесія і поля --------
class Session(Base):
    __tablename__ = "sessions"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    region_id: Mapped[int] = mapped_column(ForeignKey("regions.id"), index=True)
    preset: Mapped[str] = mapped_column(String(32), default="default")
    config_json: Mapped[dict] = mapped_column(JSONB)
    config_sha: Mapped[str | None] = mapped_column(String(64), nullable=True)
    manifests_sha: Mapped[str | None] = mapped_column(String(64), nullable=True)
    started_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    seed_rng: Mapped[int | None] = mapped_column(Integer, nullable=True)

class Field(Base):
    __tablename__ = "fields"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[int] = mapped_column(ForeignKey("sessions.id"), index=True)
    x: Mapped[int] = mapped_column(Integer)  # клетка 0..(W-1)
    y: Mapped[int] = mapped_column(Integer)  # клетка 0..(H-1)
    state: Mapped[dict | None] = mapped_column(JSONB, nullable=True)  # произвольные отметки
    fertility: Mapped[float] = mapped_column(Float, default=50.0)
    salinity: Mapped[float] = mapped_column(Float, default=10.0)
    moisture: Mapped[float] = mapped_column(Float, default=50.0)
    ndvi: Mapped[float] = mapped_column(Float, default=0.2)
    protection: Mapped[int] = mapped_column(Integer, default=0)
    __table_args__ = (UniqueConstraint("session_id", "x", "y", name="uq_field_cell"),)

# -------- Розміщення інфраструктури та посадки --------
class InfraPlacement(Base):
    __tablename__ = "infra_placements"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[int] = mapped_column(ForeignKey("sessions.id"), index=True)
    infra_id: Mapped[int] = mapped_column(ForeignKey("manifests_infrastructure.id"))
    area_mode: Mapped[str] = mapped_column(String(32))  # per_field | per_sector | farm_wide
    tiles: Mapped[list[int] | None] = mapped_column(ARRAY(Integer), nullable=True)  # список индексов клеток
    payload: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class Planting(Base):
    __tablename__ = "plantings"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[int] = mapped_column(ForeignKey("sessions.id"), index=True)
    crop_id: Mapped[int] = mapped_column(ForeignKey("manifests_crops.id"))
    field_id: Mapped[int] = mapped_column(ForeignKey("fields.id"))
    season_start: Mapped[int] = mapped_column(Integer)   # 0..(years*4-1)
    status: Mapped[str] = mapped_column(String(32), default="growing")  # growing/harvested/failed

# -------- Скот --------
class Livestock(Base):
    __tablename__ = "livestock"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[int] = mapped_column(ForeignKey("sessions.id"), index=True)
    kind: Mapped[str] = mapped_column(String(32))    # small_ruminant / cattle / pack
    headcount: Mapped[int] = mapped_column(Integer, default=0)
    paddock_tiles: Mapped[list[int] | None] = mapped_column(ARRAY(Integer), nullable=True)
    params: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

# -------- Фінанси, події, телеметрія --------
FinanceKind = Enum("loan", "subsidy", "insurance", "payment", "penalty", name="fin_kind")
EventKind = Enum("historical", "procedural", name="event_kind")

class Finance(Base):
    __tablename__ = "finances"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[int] = mapped_column(ForeignKey("sessions.id"), index=True)
    kind: Mapped[str] = mapped_column(FinanceKind)
    amount: Mapped[float] = mapped_column(Float)
    season: Mapped[int] = mapped_column(Integer)
    note: Mapped[str | None] = mapped_column(String(256), nullable=True)

class Event(Base):
    __tablename__ = "events"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[int] = mapped_column(ForeignKey("sessions.id"), index=True)
    kind: Mapped[str] = mapped_column(EventKind)
    code: Mapped[str] = mapped_column(String(64))
    payload: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    season: Mapped[int] = mapped_column(Integer)
    resolved: Mapped[bool] = mapped_column(Boolean, default=False)
    choice: Mapped[str | None] = mapped_column(String(32), nullable=True)

class Telemetry(Base):
    __tablename__ = "telemetry"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[int] = mapped_column(ForeignKey("sessions.id"), index=True)
    season: Mapped[int] = mapped_column(Integer, index=True)
    kpi: Mapped[dict] = mapped_column(JSONB)  # {water_debt:..., fertility:..., salinity:...}
