from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from .db import AsyncSessionLocal
from ..models.orm import Run, YearEconomy

class StateStore:
    """Persist run economy in Postgres (async)."""
    async def ensure_run(self, session: AsyncSession, run_id: str, region_id: str):
        obj = await session.get(Run, run_id)
        if not obj:
            session.add(Run(id=run_id, region_id=region_id))

    async def add_year(self, run_id: str, region_id: str, year: int, econ: dict):
        async with AsyncSessionLocal() as s:
            await self.ensure_run(s, run_id, region_id)
            s.add(YearEconomy(
                run_id=run_id, year=year,
                revenue=econ.get("revenue", 0.0),
                costs=econ.get("costs", 0.0),
                balance=econ.get("balance", 0.0)
            ))
            await s.commit()

    async def summary(self, run_id: str) -> dict:
        async with AsyncSessionLocal() as s:
            q = await s.execute(select(YearEconomy.balance).where(YearEconomy.run_id==run_id).order_by(YearEconomy.year))
            balances = [b for (b,) in q.all()]
            total = sum(balances)
            return {"score": {"eco": total, "env": 0.0, "total": total},
                    "charts": {"balance": balances},
                    "analysis_text": "Summary from PostgreSQL storage."}
