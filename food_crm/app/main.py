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

app = FastAPI(
    title="Food Services CRM",
    description="Multi-tenant CRM + Ops-lite with email, PDF, pipeline, and myDATA integration stub.",
    version="1.0.0",
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
