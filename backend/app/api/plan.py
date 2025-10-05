from fastapi import APIRouter
from ..models import PlanCrops, PlanLivestock, PlanDrainage, PlanPests
from ..store import saves

router = APIRouter()

@router.post("/farm/{save_id}/plan/crops")
def plan_crops(save_id: str, plan: PlanCrops):
    return saves.save_plan(save_id, "crops", plan.dict(by_alias=True))

@router.post("/farm/{save_id}/plan/livestock")
def plan_livestock(save_id: str, plan: PlanLivestock):
    return saves.save_plan(save_id, "livestock", plan.dict())

@router.post("/farm/{save_id}/plan/drainage")
def plan_drainage(save_id: str, plan: PlanDrainage):
    return saves.save_plan(save_id, "drainage", plan.dict())

@router.post("/farm/{save_id}/plan/pests")
def plan_pests(save_id: str, plan: PlanPests):
    return saves.save_plan(save_id, "pests", plan.dict())

# Legacy combined plan (deprecated)
@router.post("/farm/{save_id}/plan")
def plan_legacy(save_id: str, payload: dict):
    return saves.save_plan(save_id, "legacy", payload)