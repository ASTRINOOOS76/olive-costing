from __future__ import annotations
from datetime import datetime, date
from typing import Optional

from sqlalchemy import (
    String, Integer, DateTime, Date, Float, ForeignKey, Text,
    Index
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

def utcnow() -> datetime:
    return datetime.utcnow().replace(microsecond=0)

class Base(DeclarativeBase):
    pass

class Company(Base):
    __tablename__ = "companies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(220), nullable=False, index=True)

    country: Mapped[Optional[str]] = mapped_column(String(80))
    city: Mapped[Optional[str]] = mapped_column(String(120))
    address: Mapped[Optional[str]] = mapped_column(String(250))
    vat: Mapped[Optional[str]] = mapped_column(String(60))
    website: Mapped[Optional[str]] = mapped_column(String(200))
    email: Mapped[Optional[str]] = mapped_column(String(180))
    phone: Mapped[Optional[str]] = mapped_column(String(80))
    notes: Mapped[Optional[str]] = mapped_column(Text)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, nullable=False)

    contacts: Mapped[list["Contact"]] = relationship(back_populates="company", cascade="all, delete-orphan")
    deals: Mapped[list["Deal"]] = relationship(back_populates="company", cascade="all, delete-orphan")
    tasks: Mapped[list["Task"]] = relationship(back_populates="company", cascade="all, delete-orphan")
    activities: Mapped[list["Activity"]] = relationship(back_populates="company", cascade="all, delete-orphan")

class Contact(Base):
    __tablename__ = "contacts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    company_id: Mapped[Optional[int]] = mapped_column(ForeignKey("companies.id", ondelete="SET NULL"))

    first_name: Mapped[Optional[str]] = mapped_column(String(120))
    last_name: Mapped[Optional[str]] = mapped_column(String(120), index=True)
    title: Mapped[Optional[str]] = mapped_column(String(160))
    email: Mapped[Optional[str]] = mapped_column(String(180), index=True)
    phone: Mapped[Optional[str]] = mapped_column(String(80))
    linkedin: Mapped[Optional[str]] = mapped_column(String(220))
    notes: Mapped[Optional[str]] = mapped_column(Text)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, nullable=False)

    company: Mapped[Optional[Company]] = relationship(back_populates="contacts")
    tasks: Mapped[list["Task"]] = relationship(back_populates="contact", cascade="all, delete-orphan")
    activities: Mapped[list["Activity"]] = relationship(back_populates="contact", cascade="all, delete-orphan")

class Deal(Base):
    __tablename__ = "deals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    company_id: Mapped[Optional[int]] = mapped_column(ForeignKey("companies.id", ondelete="SET NULL"))

    title: Mapped[str] = mapped_column(String(240), nullable=False, index=True)
    stage: Mapped[str] = mapped_column(String(40), nullable=False, index=True)

    value_eur: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    probability: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)  # 0..100

    expected_close_date: Mapped[Optional[date]] = mapped_column(Date)
    source: Mapped[Optional[str]] = mapped_column(String(60))
    owner: Mapped[Optional[str]] = mapped_column(String(120))
    notes: Mapped[Optional[str]] = mapped_column(Text)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, nullable=False)

    company: Mapped[Optional[Company]] = relationship(back_populates="deals")
    tasks: Mapped[list["Task"]] = relationship(back_populates="deal", cascade="all, delete-orphan")
    activities: Mapped[list["Activity"]] = relationship(back_populates="deal", cascade="all, delete-orphan")

class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    company_id: Mapped[Optional[int]] = mapped_column(ForeignKey("companies.id", ondelete="SET NULL"))
    contact_id: Mapped[Optional[int]] = mapped_column(ForeignKey("contacts.id", ondelete="SET NULL"))
    deal_id: Mapped[Optional[int]] = mapped_column(ForeignKey("deals.id", ondelete="SET NULL"))

    title: Mapped[str] = mapped_column(String(240), nullable=False, index=True)
    due_date: Mapped[Optional[date]] = mapped_column(Date)
    status: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    priority: Mapped[int] = mapped_column(Integer, default=2, nullable=False)  # 1 high,2 normal,3 low
    owner: Mapped[Optional[str]] = mapped_column(String(120))
    notes: Mapped[Optional[str]] = mapped_column(Text)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, nullable=False)

    company: Mapped[Optional[Company]] = relationship(back_populates="tasks")
    contact: Mapped[Optional[Contact]] = relationship(back_populates="tasks")
    deal: Mapped[Optional[Deal]] = relationship(back_populates="tasks")

class Activity(Base):
    __tablename__ = "activities"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    company_id: Mapped[Optional[int]] = mapped_column(ForeignKey("companies.id", ondelete="SET NULL"))
    contact_id: Mapped[Optional[int]] = mapped_column(ForeignKey("contacts.id", ondelete="SET NULL"))
    deal_id: Mapped[Optional[int]] = mapped_column(ForeignKey("deals.id", ondelete="SET NULL"))

    activity_type: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    subject: Mapped[Optional[str]] = mapped_column(String(240))
    body: Mapped[Optional[str]] = mapped_column(Text)

    activity_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, nullable=False)

    company: Mapped[Optional[Company]] = relationship(back_populates="activities")
    contact: Mapped[Optional[Contact]] = relationship(back_populates="activities")
    deal: Mapped[Optional[Deal]] = relationship(back_populates="activities")

Index("idx_deals_stage_created", Deal.stage, Deal.created_at)
Index("idx_tasks_status_due", Task.status, Task.due_date)
Index("idx_activities_date_created", Activity.activity_date, Activity.created_at)
