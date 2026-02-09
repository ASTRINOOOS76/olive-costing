from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, UUIDMixin, TimestampMixin


class EmailMessage(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "email_messages"
    tenant_id: Mapped[str] = mapped_column(
        ForeignKey("tenants.id"), index=True, nullable=False
    )

    direction: Mapped[str] = mapped_column(
        String(10), default="out"
    )  # out / in
    subject: Mapped[str | None] = mapped_column(String(500))
    sender: Mapped[str | None] = mapped_column(String(255))
    recipients: Mapped[str | None] = mapped_column(String(2000))
    cc: Mapped[str | None] = mapped_column(String(2000))

    provider_msg_id: Mapped[str | None] = mapped_column(String(255), index=True)
    thread_id: Mapped[str | None] = mapped_column(String(255), index=True)
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    body_text: Mapped[str | None] = mapped_column(Text)
    body_html: Mapped[str | None] = mapped_column(Text)

    # optional polymorphic linking
    entity_type: Mapped[str | None] = mapped_column(
        String(30)
    )  # company / contact / quote / po / deal
    entity_id: Mapped[str | None] = mapped_column(String(60), index=True)
