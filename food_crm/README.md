# Food Services CRM

Multi-tenant CRM + Ops-lite platform (FastAPI + PostgreSQL + Celery).

## Modules

| Module | Description |
|---|---|
| **Tenants / Users / RBAC** | Multi-tenant with owner/admin/sales/ops/viewer roles |
| **Companies** | Customers & suppliers (flags) |
| **Contacts** | Linked to companies |
| **Deals / Pipeline** | lead → qualified → proposal → negotiation → won/lost |
| **Activities** | Tasks, calls, meetings – linked to any entity |
| **Items** | Products/services catalogue |
| **Price Lists** | Per-tenant price lists with MOQ |
| **Quotes** | Quotations with PDF generation |
| **Purchase Orders** | POs to suppliers with PDF generation |
| **Email (SMTP)** | Send emails with attachments, logged in CRM |
| **Email (IMAP)** | Inbound sync worker, auto-link to company/contact |
| **Invoicing** | Stub module ready for ΑΑΔΕ/myDATA integration |

## Quick Start

```bash
# 1) Start infrastructure
docker compose up -d

# 2) Python virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 3) Run database migrations
alembic upgrade head

# 4) Start API server
uvicorn app.main:app --reload

# 5) Start background worker (IMAP sync + invoicing)
celery -A app.workers.celery_app.celery_app worker -Q email,invoicing --loglevel=INFO
```

## API Docs

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## First Steps

1. **Register a tenant**: `POST /auth/register` with `tenant_name`, `email`, `password`
2. **Login**: `POST /auth/login` with `tenant_id`, `email`, `password` → get JWT
3. Use the JWT as Bearer token for all subsequent API calls

## Architecture

```
app/
  core/       # config, db, security, deps, rbac
  models/     # SQLAlchemy ORM models
  schemas/    # Pydantic request/response schemas
  routers/    # FastAPI route handlers
  services/   # PDF generation, SMTP, IMAP sync, myDATA
  workers/    # Celery app + async tasks
```

## myDATA / ΑΑΔΕ Integration

The invoicing module includes a provider interface (`app/services/mydata.py`).
Currently a stub — swap `MyDataProviderStub` with a real implementation when ready.
The database already has `invoices`, `invoice_lines`, and `mydata_submissions` tables
with full audit trail support.
