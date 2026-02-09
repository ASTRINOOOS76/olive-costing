from datetime import datetime

from pydantic import BaseModel


class ActivityIn(BaseModel):
    activity_type: str = "task"  # task / call / meeting / email
    subject: str
    description: str | None = None
    due_at: datetime | None = None
    assigned_to: str | None = None
    entity_type: str | None = None
    entity_id: str | None = None


class ActivityOut(ActivityIn):
    id: str
    tenant_id: str
    completed_at: datetime | None = None

    class Config:
        from_attributes = True


class ActivityComplete(BaseModel):
    completed_at: datetime | None = None
