from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql as pg

revision = "20251005_0001_init"
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # enums
    fin_kind = sa.Enum("loan","subsidy","insurance","payment","penalty", name="fin_kind")
    event_kind = sa.Enum("historical","procedural", name="event_kind")
    fin_kind.create(op.get_bind(), checkfirst=True)
    event_kind.create(op.get_bind(), checkfirst=True)

    op.create_table("manifests_infrastructure",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("key", sa.String(64), nullable=False, unique=True),
        sa.Column("json", pg.JSONB, nullable=False),
        sa.Column("category", sa.String(64), nullable=False),
        sa.Column("sustainable", sa.Boolean, nullable=False, server_default=sa.text("false")),
        sa.Column("regions", pg.ARRAY(sa.String(64))),
        sa.Column("capex_usd_per_ha", sa.Float),
        sa.Column("opex_usd_per_ha_per_season", sa.Float),
        sa.Column("version", sa.String(32)),
        sa.Column("updated_at", sa.DateTime, server_default=sa.text("now()")),
    )

    op.create_table("manifests_crops",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("key", sa.String(64), nullable=False, unique=True),
        sa.Column("json", pg.JSONB, nullable=False),
        sa.Column("region", sa.String(64), index=True),
        sa.Column("base_yield", sa.Float),
        sa.Column("water_req", sa.Float),
        sa.Column("price_usd_per_ton", sa.Float),
        sa.Column("version", sa.String(32)),
        sa.Column("updated_at", sa.DateTime, server_default=sa.text("now()")),
    )

    op.create_table("regions",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.String(128), nullable=False, unique=True),
        sa.Column("bbox_json", pg.JSONB),
        sa.Column("grid_w", sa.Integer, nullable=False, server_default="200"),
        sa.Column("grid_h", sa.Integer, nullable=False, server_default="200"),
        sa.Column("tile_m", sa.Integer, nullable=False, server_default="250"),
        sa.Column("meta_json", pg.JSONB),
    )

    op.create_table("region_allowed_crops",
        sa.Column("region_id", sa.Integer, sa.ForeignKey("regions.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("crop_id", sa.Integer, sa.ForeignKey("manifests_crops.id", ondelete="CASCADE"), primary_key=True),
    )

    op.create_table("sessions",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("region_id", sa.Integer, sa.ForeignKey("regions.id"), index=True),
        sa.Column("preset", sa.String(32), nullable=False, server_default="default"),
        sa.Column("config_json", pg.JSONB, nullable=False),
        sa.Column("config_sha", sa.String(64)),
        sa.Column("manifests_sha", sa.String(64)),
        sa.Column("started_at", sa.DateTime, server_default=sa.text("now()")),
        sa.Column("finished_at", sa.DateTime),
        sa.Column("seed_rng", sa.Integer),
    )

    op.create_table("fields",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("session_id", sa.Integer, sa.ForeignKey("sessions.id", ondelete="CASCADE"), index=True),
        sa.Column("x", sa.Integer, nullable=False),
        sa.Column("y", sa.Integer, nullable=False),
        sa.Column("state", pg.JSONB),
        sa.Column("fertility", sa.Float, nullable=False, server_default="50"),
        sa.Column("salinity", sa.Float, nullable=False, server_default="10"),
        sa.Column("moisture", sa.Float, nullable=False, server_default="50"),
        sa.Column("ndvi", sa.Float, nullable=False, server_default="0.2"),
        sa.Column("protection", sa.Integer, nullable=False, server_default="0"),
        sa.UniqueConstraint("session_id","x","y", name="uq_field_cell"),
    )

    op.create_table("infra_placements",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("session_id", sa.Integer, sa.ForeignKey("sessions.id", ondelete="CASCADE"), index=True),
        sa.Column("infra_id", sa.Integer, sa.ForeignKey("manifests_infrastructure.id")),
        sa.Column("area_mode", sa.String(32), nullable=False),
        sa.Column("tiles", pg.ARRAY(sa.Integer)),
        sa.Column("payload", pg.JSONB),
        sa.Column("created_at", sa.DateTime, server_default=sa.text("now()")),
    )

    op.create_table("plantings",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("session_id", sa.Integer, sa.ForeignKey("sessions.id", ondelete="CASCADE"), index=True),
        sa.Column("crop_id", sa.Integer, sa.ForeignKey("manifests_crops.id")),
        sa.Column("field_id", sa.Integer, sa.ForeignKey("fields.id", ondelete="CASCADE")),
        sa.Column("season_start", sa.Integer, nullable=False),
        sa.Column("status", sa.String(32), nullable=False, server_default="growing"),
    )

    op.create_table("livestock",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("session_id", sa.Integer, sa.ForeignKey("sessions.id", ondelete="CASCADE"), index=True),
        sa.Column("kind", sa.String(32), nullable=False),
        sa.Column("headcount", sa.Integer, nullable=False, server_default="0"),
        sa.Column("paddock_tiles", pg.ARRAY(sa.Integer)),
        sa.Column("params", pg.JSONB),
    )

    op.create_table("finances",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("session_id", sa.Integer, sa.ForeignKey("sessions.id", ondelete="CASCADE"), index=True),
        sa.Column("kind", sa.Enum(name="fin_kind", create_type=False)),
        sa.Column("amount", sa.Float, nullable=False),
        sa.Column("season", sa.Integer, nullable=False),
        sa.Column("note", sa.String(256)),
    )

    op.create_table("events",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("session_id", sa.Integer, sa.ForeignKey("sessions.id", ondelete="CASCADE"), index=True),
        sa.Column("kind", sa.Enum(name="event_kind", create_type=False)),
        sa.Column("code", sa.String(64), nullable=False),
        sa.Column("payload", pg.JSONB),
        sa.Column("season", sa.Integer, nullable=False),
        sa.Column("resolved", sa.Boolean, nullable=False, server_default=sa.text("false")),
        sa.Column("choice", sa.String(32)),
    )

    op.create_table("telemetry",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("session_id", sa.Integer, sa.ForeignKey("sessions.id", ondelete="CASCADE"), index=True),
        sa.Column("season", sa.Integer, nullable=False, index=True),
        sa.Column("kpi", pg.JSONB, nullable=False),
    )

def downgrade():
    op.drop_table("telemetry")
    op.drop_table("events")
    op.drop_table("finances")
    op.drop_table("livestock")
    op.drop_table("plantings")
    op.drop_table("infra_placements")
    op.drop_table("fields")
    op.drop_table("sessions")
    op.drop_table("region_allowed_crops")
    op.drop_table("regions")
    op.drop_table("manifests_crops")
    op.drop_table("manifests_infrastructure")
    sa.Enum(name="event_kind").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="fin_kind").drop(op.get_bind(), checkfirst=True)
