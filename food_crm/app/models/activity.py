from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, UUIDMixin, TimestampMixin


class Activity(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "activities"
    tenant_id: Mapped[str] = mapped_column(
        ForeignKey("tenants.id"), index=True, nullable=False
    )
    assigned_to: Mapped[str | None] = mapped_column(
        ForeignKey("users.id"), index=True
    )

    activity_type: Mapped[str] = mapped_column(
        String(30), default="task"
    )  # task / call / meeting / email
    subject: Mapped[str] = mapped_column(String(300), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)

    due_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    # polymorphic link
    entity_type: Mapped[str | None] = mapped_column(
        String(30)
    )  # company / contact / deal / quote / po
    entity_id: Mapped[str | None] = mapped_column(String(60), index=True)
