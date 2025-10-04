from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer, Float, ForeignKey
from ..services.db import Base

class Run(Base):
    __tablename__ = "runs"
    id: Mapped[str] = mapped_column(String(40), primary_key=True)
    region_id: Mapped[str] = mapped_column(String(64))

class YearEconomy(Base):
    __tablename__ = "year_economy"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    run_id: Mapped[str] = mapped_column(ForeignKey("runs.id", ondelete="CASCADE"))
    year: Mapped[int] = mapped_column(Integer)
    revenue: Mapped[float] = mapped_column(Float)
    costs: Mapped[float] = mapped_column(Float)
    balance: Mapped[float] = mapped_column(Float)
