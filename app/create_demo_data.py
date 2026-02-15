"""
Script to populate the database with demo data for testing the CRM application.
Run this script once to insert demo tenants, users, companies, contacts, deals, etc.
"""

from app.core.db import SessionLocal
from app.models import tenant, user, company, contact, deal, activity, item
from sqlalchemy.exc import IntegrityError

def create_demo_data():
    db = SessionLocal()
    try:
        # Tenant
        t = tenant.Tenant(name="Demo Tenant")
        db.add(t)
        db.flush()  # get t.id

        # User
        u = user.User(tenant_id=t.id, email="demo@demo.com", password_hash="demo", role="admin")
        db.add(u)
        db.flush()

        # Company
        c = company.Company(tenant_id=t.id, name="Demo Company", vat="GR123456789", country="GR", email="info@demo.com", phone="2101234567", address="Athens, Greece", is_customer=True, is_supplier=False)
        db.add(c)
        db.flush()

        # Contact
        ct = contact.Contact(tenant_id=t.id, company_id=c.id, first_name="John", last_name="Doe", email="john.doe@demo.com")
        db.add(ct)
        db.flush()

        # Deal
        d = deal.Deal(tenant_id=t.id, company_id=c.id, contact_id=ct.id, assigned_to=u.id, title="Demo Deal", stage="lead", value=10000, currency="EUR", notes="Demo deal notes")
        db.add(d)
        db.flush()

        # Activity
        a = activity.Activity(tenant_id=t.id, assigned_to=u.id, activity_type="task", subject="Call John Doe", description="Initial call", entity_type="contact")
        db.add(a)
        db.flush()

        # Item
        i = item.Item(tenant_id=t.id, sku="SKU001", name="Demo Item", unit="pcs", vat_rate=24)
        db.add(i)
        db.commit()
        print("Demo data created successfully.")
    except IntegrityError:
        db.rollback()
        print("Demo data already exists or error occurred.")
    finally:
        db.close()

if __name__ == "__main__":
    create_demo_data()
