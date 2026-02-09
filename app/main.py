from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.routers import (
    activities,
    auth,
    companies,
    contacts,
    deals,
    emails,
    health,
    items,
    pricelists,
    purchase_orders,
    quotes,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create all tables on startup (dev convenience; use Alembic in prod)
    from app.core.db import engine
    from app.models.base import Base  # noqa: F401
    # Import every model so Base.metadata knows about them
    import app.models.tenant  # noqa: F401
    import app.models.user  # noqa: F401
    import app.models.company  # noqa: F401
    import app.models.contact  # noqa: F401
    import app.models.deal  # noqa: F401
    import app.models.activity  # noqa: F401
    import app.models.item  # noqa: F401
    import app.models.pricelist  # noqa: F401
    import app.models.quote  # noqa: F401
    import app.models.po  # noqa: F401
    import app.models.emailmsg  # noqa: F401
    import app.models.invoice  # noqa: F401

    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Food Services CRM",
    description="Multi-tenant CRM + Ops-lite with email, PDF, pipeline, and myDATA integration stub.",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(health.router)
app.include_router(auth.router)
app.include_router(companies.router)
app.include_router(contacts.router)
app.include_router(deals.router)
app.include_router(activities.router)
app.include_router(items.router)
app.include_router(pricelists.router)
app.include_router(quotes.router)
app.include_router(purchase_orders.router)
app.include_router(emails.router)
