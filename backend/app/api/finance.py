from fastapi import APIRouter
from pydantic import BaseModel
from ..store import saves

router = APIRouter()

class LoanReq(BaseModel):
    amount: float
    term: int

class InsureReq(BaseModel):
    coverage: str
    sum: float

@router.post("/finance/{save_id}/loan")
def loan(save_id: str, req: LoanReq):
    return saves.add_loan(save_id, req.dict())

@router.post("/finance/{save_id}/insure")
def insure(save_id: str, req: InsureReq):
    return saves.add_insurance(save_id, req.dict())

@router.get("/finance/{save_id}/report")
def report(save_id: str, year: int | None = None):
    return saves.finance_report(save_id, year)