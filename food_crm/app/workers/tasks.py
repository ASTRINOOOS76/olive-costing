import re

from sqlalchemy.orm import Session

from app.core.db import SessionLocal
from app.models.company import Company
from app.models.emailmsg import EmailMessage
from app.services.imap_sync import fetch_latest_emails
from app.workers.celery_app import celery_app


def _extract_email(s: str | None) -> str | None:
    if not s:
        return None
    m = re.search(r"[\w\.\-]+@[\w\.\-]+\.\w+", s)
    return m.group(0).lower() if m else None


@celery_app.task
def imap_sync_task(tenant_id: str, limit: int = 50):
    """Fetch emails from IMAP and persist them, auto-linking to companies."""
    db: Session = SessionLocal()
    try:
        msgs = fetch_latest_emails(limit=limit)
        for m in msgs:
            provider_id = m.get("provider_msg_id")
            if not provider_id:
                continue

            exists = (
                db.query(EmailMessage)
                .filter(
                    EmailMessage.tenant_id == tenant_id,
                    EmailMessage.provider_msg_id == provider_id,
                )
                .first()
            )
            if exists:
                continue

            # auto-link by sender email → company.email
            sender_email = _extract_email(m.get("from"))
            entity_type = None
            entity_id = None
            if sender_email:
                comp = (
                    db.query(Company)
                    .filter(
                        Company.tenant_id == tenant_id,
                        Company.email == sender_email,
                    )
                    .first()
                )
                if comp:
                    entity_type, entity_id = "company", comp.id

            em = EmailMessage(
                tenant_id=tenant_id,
                direction="in",
                subject=m.get("subject"),
                sender=m.get("from"),
                recipients=m.get("to"),
                cc=m.get("cc"),
                provider_msg_id=provider_id,
                thread_id=m.get("thread_id"),
                body_text=m.get("body_text"),
                body_html=m.get("body_html"),
                entity_type=entity_type,
                entity_id=entity_id,
            )
            db.add(em)
        db.commit()
    finally:
        db.close()


@celery_app.task
def mydata_submit_task(tenant_id: str, invoice_id: str):
    """Stub: later calls mydata_provider.submit_invoice()."""
    return {
        "tenant_id": tenant_id,
        "invoice_id": invoice_id,
        "status": "stubbed",
    }
