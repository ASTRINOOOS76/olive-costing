from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import get_ctx, get_db
from app.core.rbac import require_perm
from app.models.activity import Activity
from app.schemas.activity import ActivityComplete, ActivityIn, ActivityOut

router = APIRouter(prefix="/activities", tags=["activities"])


@router.get("", response_model=list[ActivityOut])
def list_activities(
    entity_type: str | None = None,
    entity_id: str | None = None,
    assigned_to: str | None = None,
    db: Session = Depends(get_db),
    ctx: dict = Depends(get_ctx),
):
    require_perm(ctx["role"], "activities:read")
    q = db.query(Activity).filter(Activity.tenant_id == ctx["tenant_id"])
    if entity_type:
        q = q.filter(Activity.entity_type == entity_type)
    if entity_id:
        q = q.filter(Activity.entity_id == entity_id)
    if assigned_to:
        q = q.filter(Activity.assigned_to == assigned_to)
    return q.order_by(Activity.due_at.desc().nullslast()).all()


@router.get("/{activity_id}", response_model=ActivityOut)
def get_activity(
    activity_id: str,
    db: Session = Depends(get_db),
    ctx: dict = Depends(get_ctx),
):
    require_perm(ctx["role"], "activities:read")
    a = db.get(Activity, activity_id)
    if not a or a.tenant_id != ctx["tenant_id"]:
        raise HTTPException(404, "Activity not found")
    return a


@router.post("", response_model=ActivityOut)
def create_activity(
    payload: ActivityIn,
    db: Session = Depends(get_db),
    ctx: dict = Depends(get_ctx),
):
    require_perm(ctx["role"], "activities:create")
    a = Activity(tenant_id=ctx["tenant_id"], **payload.model_dump())
    db.add(a)
    db.commit()
    db.refresh(a)
    return a


@router.put("/{activity_id}", response_model=ActivityOut)
def update_activity(
    activity_id: str,
    payload: ActivityIn,
    db: Session = Depends(get_db),
    ctx: dict = Depends(get_ctx),
):
    require_perm(ctx["role"], "activities:update")
    a = db.get(Activity, activity_id)
    if not a or a.tenant_id != ctx["tenant_id"]:
        raise HTTPException(404, "Activity not found")
    for k, v in payload.model_dump().items():
        setattr(a, k, v)
    db.commit()
    db.refresh(a)
    return a


@router.patch("/{activity_id}/complete", response_model=ActivityOut)
def complete_activity(
    activity_id: str,
    payload: ActivityComplete | None = None,
    db: Session = Depends(get_db),
    ctx: dict = Depends(get_ctx),
):
    require_perm(ctx["role"], "activities:update")
    a = db.get(Activity, activity_id)
    if not a or a.tenant_id != ctx["tenant_id"]:
        raise HTTPException(404, "Activity not found")
    a.completed_at = (
        payload.completed_at if payload and payload.completed_at else datetime.now(timezone.utc)
    )
    db.commit()
    db.refresh(a)
    return a


@router.delete("/{activity_id}")
def delete_activity(
    activity_id: str,
    db: Session = Depends(get_db),
    ctx: dict = Depends(get_ctx),
):
    require_perm(ctx["role"], "activities:delete")
    a = db.get(Activity, activity_id)
    if not a or a.tenant_id != ctx["tenant_id"]:
        raise HTTPException(404, "Activity not found")
    db.delete(a)
    db.commit()
    return {"ok": True}
