from __future__ import annotations
import os
from datetime import date, datetime
from typing import Optional, List, Literal, Any

from fastapi import FastAPI, Depends, HTTPException, Header, Query
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings

from sqlalchemy import create_engine, select, func, or_
from sqlalchemy.orm import sessionmaker, Session

from models import Base, Company, Contact, Deal, Task, Activity

PIPELINE_STAGES = ["Lead", "Qualified", "Proposal", "Negotiation", "Won", "Lost"]
TASK_STATUS = ["Open", "In Progress", "Done", "Blocked"]
ACTIVITY_TYPES = ["Call", "Email", "Meeting", "Note", "Task", "WhatsApp", "Other"]

class Settings(BaseSettings):
    database_url: str = Field(default="sqlite:///./crm.sqlite3", alias="DATABASE_URL")
    api_key: str = Field(default="change-me-now", alias="API_KEY")

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()

engine = create_engine(settings.database_url, echo=False, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)

def init_db():
    Base.metadata.create_all(engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def auth(x_api_key: Optional[str] = Header(default=None), authorization: Optional[str] = Header(default=None)):
    # Accept either X-API-Key or "Authorization: Bearer <key>"
    key = None
    if x_api_key:
        key = x_api_key.strip()
    elif authorization and authorization.lower().startswith("bearer "):
        key = authorization[7:].strip()
    if not key or key != settings.api_key:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return True

def not_found(entity: str):
    raise HTTPException(status_code=404, detail=f"{entity} not found")

# ----------------- Schemas -----------------
class CompanyIn(BaseModel):
    name: str
    country: Optional[str] = None
    city: Optional[str] = None
    address: Optional[str] = None
    vat: Optional[str] = None
    website: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    notes: Optional[str] = None

class CompanyOut(CompanyIn):
    id: int
    created_at: datetime

class ContactIn(BaseModel):
    company_id: Optional[int] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    title: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    linkedin: Optional[str] = None
    notes: Optional[str] = None

class ContactOut(ContactIn):
    id: int
    created_at: datetime

class DealIn(BaseModel):
    company_id: Optional[int] = None
    title: str
    stage: str
    value_eur: float = 0.0
    probability: float = 0.0
    expected_close_date: Optional[date] = None
    source: Optional[str] = None
    owner: Optional[str] = None
    notes: Optional[str] = None

class DealOut(DealIn):
    id: int
    created_at: datetime

class TaskIn(BaseModel):
    company_id: Optional[int] = None
    contact_id: Optional[int] = None
    deal_id: Optional[int] = None
    title: str
    due_date: Optional[date] = None
    status: str
    priority: int = 2
    owner: Optional[str] = None
    notes: Optional[str] = None

class TaskOut(TaskIn):
    id: int
    created_at: datetime

class ActivityIn(BaseModel):
    company_id: Optional[int] = None
    contact_id: Optional[int] = None
    deal_id: Optional[int] = None
    activity_type: str
    subject: Optional[str] = None
    body: Optional[str] = None
    activity_date: date

class ActivityOut(ActivityIn):
    id: int
    created_at: datetime

class KPIOut(BaseModel):
    companies: int
    contacts: int
    deals: int
    open_tasks: int
    pipeline_total: float
    pipeline_weighted: float

# ----------------- App -----------------
app = FastAPI(title="CRM API", version="2.0")

@app.on_event("startup")
def _startup():
    init_db()

# Health
@app.get("/health")
def health():
    return {"ok": True}

# KPIs
@app.get("/kpi", response_model=KPIOut, dependencies=[Depends(auth)])
def kpi(db: Session = Depends(get_db)):
    companies = db.scalar(select(func.count()).select_from(Company)) or 0
    contacts = db.scalar(select(func.count()).select_from(Contact)) or 0
    deals = db.scalar(select(func.count()).select_from(Deal)) or 0
    open_tasks = db.scalar(select(func.count()).select_from(Task).where(Task.status != "Done")) or 0

    total = db.scalar(select(func.coalesce(func.sum(Deal.value_eur), 0.0))) or 0.0
    weighted = db.scalar(select(func.coalesce(func.sum(Deal.value_eur * (Deal.probability/100.0)), 0.0))) or 0.0

    return KPIOut(
        companies=int(companies),
        contacts=int(contacts),
        deals=int(deals),
        open_tasks=int(open_tasks),
        pipeline_total=float(total),
        pipeline_weighted=float(weighted),
    )

# -------- Companies --------
@app.get("/companies", response_model=List[CompanyOut], dependencies=[Depends(auth)])
def companies_list(
    q: str = Query(default="", description="Search"),
    limit: int = Query(default=200, ge=1, le=2000),
    db: Session = Depends(get_db)
):
    stmt = select(Company).order_by(Company.name.asc()).limit(limit)
    if q.strip():
        like = f"%{q.strip()}%"
        stmt = select(Company).where(
            or_(
                Company.name.like(like),
                Company.country.like(like),
                Company.city.like(like),
                Company.vat.like(like),
            )
        ).order_by(Company.name.asc()).limit(limit)
    rows = db.scalars(stmt).all()
    return [CompanyOut(**r.__dict__) for r in rows]

@app.post("/companies", response_model=CompanyOut, dependencies=[Depends(auth)])
def companies_create(payload: CompanyIn, db: Session = Depends(get_db)):
    if not payload.name.strip():
        raise HTTPException(400, "name is required")
    row = Company(**payload.model_dump())
    db.add(row)
    db.commit()
    db.refresh(row)
    return CompanyOut(**row.__dict__)

@app.put("/companies/{company_id}", response_model=CompanyOut, dependencies=[Depends(auth)])
def companies_update(company_id: int, payload: CompanyIn, db: Session = Depends(get_db)):
    row = db.get(Company, company_id)
    if not row:
        not_found("company")
    for k, v in payload.model_dump().items():
        setattr(row, k, v)
    db.commit()
    db.refresh(row)
    return CompanyOut(**row.__dict__)

@app.delete("/companies/{company_id}", dependencies=[Depends(auth)])
def companies_delete(company_id: int, db: Session = Depends(get_db)):
    row = db.get(Company, company_id)
    if not row:
        not_found("company")
    db.delete(row)
    db.commit()
    return {"deleted": True}

# -------- Contacts --------
@app.get("/contacts", response_model=List[ContactOut], dependencies=[Depends(auth)])
def contacts_list(
    q: str = Query(default=""),
    company_id: Optional[int] = Query(default=None),
    limit: int = Query(default=500, ge=1, le=5000),
    db: Session = Depends(get_db),
):
    stmt = select(Contact).order_by(Contact.last_name.asc(), Contact.first_name.asc()).limit(limit)
    if company_id:
        stmt = stmt.where(Contact.company_id == company_id)
    if q.strip():
        like = f"%{q.strip()}%"
        stmt = stmt.where(
            or_(
                Contact.first_name.like(like),
                Contact.last_name.like(like),
                Contact.email.like(like),
                Contact.phone.like(like),
            )
        )
    rows = db.scalars(stmt).all()
    return [ContactOut(**r.__dict__) for r in rows]

@app.post("/contacts", response_model=ContactOut, dependencies=[Depends(auth)])
def contacts_create(payload: ContactIn, db: Session = Depends(get_db)):
    row = Contact(**payload.model_dump())
    db.add(row)
    db.commit()
    db.refresh(row)
    return ContactOut(**row.__dict__)

@app.put("/contacts/{contact_id}", response_model=ContactOut, dependencies=[Depends(auth)])
def contacts_update(contact_id: int, payload: ContactIn, db: Session = Depends(get_db)):
    row = db.get(Contact, contact_id)
    if not row:
        not_found("contact")
    for k, v in payload.model_dump().items():
        setattr(row, k, v)
    db.commit()
    db.refresh(row)
    return ContactOut(**row.__dict__)

@app.delete("/contacts/{contact_id}", dependencies=[Depends(auth)])
def contacts_delete(contact_id: int, db: Session = Depends(get_db)):
    row = db.get(Contact, contact_id)
    if not row:
        not_found("contact")
    db.delete(row)
    db.commit()
    return {"deleted": True}

# -------- Deals --------
@app.get("/deals", response_model=List[DealOut], dependencies=[Depends(auth)])
def deals_list(
    q: str = Query(default=""),
    stage: str = Query(default="All"),
    company_id: Optional[int] = Query(default=None),
    limit: int = Query(default=500, ge=1, le=5000),
    db: Session = Depends(get_db),
):
    stmt = select(Deal).order_by(Deal.created_at.desc()).limit(limit)
    if stage != "All":
        stmt = stmt.where(Deal.stage == stage)
    if company_id:
        stmt = stmt.where(Deal.company_id == company_id)
    if q.strip():
        like = f"%{q.strip()}%"
        stmt = stmt.where(or_(Deal.title.like(like), Deal.owner.like(like)))
    rows = db.scalars(stmt).all()
    return [DealOut(**r.__dict__) for r in rows]

@app.post("/deals", response_model=DealOut, dependencies=[Depends(auth)])
def deals_create(payload: DealIn, db: Session = Depends(get_db)):
    if payload.stage not in PIPELINE_STAGES:
        raise HTTPException(400, f"stage must be one of {PIPELINE_STAGES}")
    if payload.probability < 0 or payload.probability > 100:
        raise HTTPException(400, "probability must be 0..100")
    row = Deal(**payload.model_dump())
    db.add(row)
    db.commit()
    db.refresh(row)
    return DealOut(**row.__dict__)

@app.put("/deals/{deal_id}", response_model=DealOut, dependencies=[Depends(auth)])
def deals_update(deal_id: int, payload: DealIn, db: Session = Depends(get_db)):
    row = db.get(Deal, deal_id)
    if not row:
        not_found("deal")
    if payload.stage not in PIPELINE_STAGES:
        raise HTTPException(400, f"stage must be one of {PIPELINE_STAGES}")
    if payload.probability < 0 or payload.probability > 100:
        raise HTTPException(400, "probability must be 0..100")
    for k, v in payload.model_dump().items():
        setattr(row, k, v)
    db.commit()
    db.refresh(row)
    return DealOut(**row.__dict__)

@app.delete("/deals/{deal_id}", dependencies=[Depends(auth)])
def deals_delete(deal_id: int, db: Session = Depends(get_db)):
    row = db.get(Deal, deal_id)
    if not row:
        not_found("deal")
    db.delete(row)
    db.commit()
    return {"deleted": True}

# -------- Tasks --------
@app.get("/tasks", response_model=List[TaskOut], dependencies=[Depends(auth)])
def tasks_list(
    status: str = Query(default="All"),
    owner: str = Query(default=""),
    due_before: Optional[date] = Query(default=None),
    limit: int = Query(default=1000, ge=1, le=5000),
    db: Session = Depends(get_db),
):
    stmt = select(Task).order_by(Task.priority.asc(), Task.due_date.asc().nullslast(), Task.created_at.desc()).limit(limit)
    if status != "All":
        stmt = stmt.where(Task.status == status)
    if owner.strip():
        stmt = stmt.where(Task.owner.like(f"%{owner.strip()}%"))
    if due_before:
        stmt = stmt.where(Task.due_date != None).where(Task.due_date <= due_before)
    rows = db.scalars(stmt).all()
    return [TaskOut(**r.__dict__) for r in rows]

@app.post("/tasks", response_model=TaskOut, dependencies=[Depends(auth)])
def tasks_create(payload: TaskIn, db: Session = Depends(get_db)):
    if payload.status not in TASK_STATUS:
        raise HTTPException(400, f"status must be one of {TASK_STATUS}")
    if payload.priority not in (1,2,3):
        raise HTTPException(400, "priority must be 1,2,3")
    row = Task(**payload.model_dump())
    db.add(row)
    db.commit()
    db.refresh(row)
    return TaskOut(**row.__dict__)

@app.put("/tasks/{task_id}", response_model=TaskOut, dependencies=[Depends(auth)])
def tasks_update(task_id: int, payload: TaskIn, db: Session = Depends(get_db)):
    row = db.get(Task, task_id)
    if not row:
        not_found("task")
    if payload.status not in TASK_STATUS:
        raise HTTPException(400, f"status must be one of {TASK_STATUS}")
    if payload.priority not in (1,2,3):
        raise HTTPException(400, "priority must be 1,2,3")
    for k, v in payload.model_dump().items():
        setattr(row, k, v)
    db.commit()
    db.refresh(row)
    return TaskOut(**row.__dict__)

@app.delete("/tasks/{task_id}", dependencies=[Depends(auth)])
def tasks_delete(task_id: int, db: Session = Depends(get_db)):
    row = db.get(Task, task_id)
    if not row:
        not_found("task")
    db.delete(row)
    db.commit()
    return {"deleted": True}

# -------- Activities --------
@app.get("/activities", response_model=List[ActivityOut], dependencies=[Depends(auth)])
def activities_list(
    q: str = Query(default=""),
    days: int = Query(default=30, ge=1, le=3650),
    limit: int = Query(default=2000, ge=1, le=10000),
    db: Session = Depends(get_db),
):
    cutoff = date.fromordinal(date.today().toordinal() - days)
    stmt = select(Activity).where(Activity.activity_date >= cutoff).order_by(Activity.activity_date.desc(), Activity.created_at.desc()).limit(limit)
    if q.strip():
        like = f"%{q.strip()}%"
        stmt = stmt.where(or_(Activity.subject.like(like), Activity.body.like(like), Activity.activity_type.like(like)))
    rows = db.scalars(stmt).all()
    return [ActivityOut(**r.__dict__) for r in rows]

@app.post("/activities", response_model=ActivityOut, dependencies=[Depends(auth)])
def activities_create(payload: ActivityIn, db: Session = Depends(get_db)):
    if payload.activity_type not in ACTIVITY_TYPES:
        raise HTTPException(400, f"activity_type must be one of {ACTIVITY_TYPES}")
    row = Activity(**payload.model_dump())
    db.add(row)
    db.commit()
    db.refresh(row)
    return ActivityOut(**row.__dict__)

@app.delete("/activities/{activity_id}", dependencies=[Depends(auth)])
def activities_delete(activity_id: int, db: Session = Depends(get_db)):
    row = db.get(Activity, activity_id)
    if not row:
        not_found("activity")
    db.delete(row)
    db.commit()
    return {"deleted": True}
