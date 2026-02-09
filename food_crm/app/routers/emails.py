import base64

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.deps import get_ctx, get_db
from app.core.rbac import require_perm
from app.models.emailmsg import EmailMessage
from app.services.mailer import send_smtp

router = APIRouter(prefix="/emails", tags=["emails"])


class SendEmailIn(BaseModel):
    to: list[str]
    cc: list[str] | None = None
    subject: str
    body: str
    entity_type: str | None = None
    entity_id: str | None = None
    attachments: list[dict] | None = None  # [{"filename":..., "b64":..., "mime":...}]


class EmailOut(BaseModel):
    id: str
    tenant_id: str
    direction: str
    subject: str | None
    sender: str | None
    recipients: str | None
    entity_type: str | None
    entity_id: str | None

    class Config:
        from_attributes = True


@router.post("/send")
def send_email(
    payload: SendEmailIn,
    db: Session = Depends(get_db),
    ctx: dict = Depends(get_ctx),
):
    require_perm(ctx["role"], "emails:send")

    atts = []
    if payload.attachments:
        for a in payload.attachments:
            atts.append(
                (
                    a["filename"],
                    base64.b64decode(a["b64"]),
                    a.get("mime", "application/octet-stream"),
                )
            )

    try:
        send_smtp(payload.subject, payload.body, payload.to, payload.cc, atts)
    except Exception as e:
        raise HTTPException(500, f"SMTP failed: {e}")

    em = EmailMessage(
        tenant_id=ctx["tenant_id"],
        direction="out",
        subject=payload.subject,
        sender=None,
        recipients=";".join(payload.to),
        cc=";".join(payload.cc) if payload.cc else None,
        body_text=payload.body,
        entity_type=payload.entity_type,
        entity_id=payload.entity_id,
    )
    db.add(em)
    db.commit()
    return {"ok": True}


@router.get("", response_model=list[EmailOut])
def list_emails(
    direction: str | None = None,
    entity_type: str | None = None,
    entity_id: str | None = None,
    db: Session = Depends(get_db),
    ctx: dict = Depends(get_ctx),
):
    require_perm(ctx["role"], "emails:read")
    q = db.query(EmailMessage).filter(EmailMessage.tenant_id == ctx["tenant_id"])
    if direction:
        q = q.filter(EmailMessage.direction == direction)
    if entity_type:
        q = q.filter(EmailMessage.entity_type == entity_type)
    if entity_id:
        q = q.filter(EmailMessage.entity_id == entity_id)
    return q.order_by(EmailMessage.created_at.desc()).limit(200).all()
