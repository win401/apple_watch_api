from datetime import date as date_type, datetime
from typing import Optional

from sqlalchemy import Boolean, Date, DateTime, Float, ForeignKey, Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class UserDB(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)


class HealthRecordDB(Base):
    __tablename__ = "health_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    date: Mapped[date_type] = mapped_column(Date, nullable=False)
    weight: Mapped[float] = mapped_column(Float, nullable=False)
    height: Mapped[float] = mapped_column(Float, nullable=False)
    systolic: Mapped[int] = mapped_column(Integer, nullable=False)
    diastolic: Mapped[int] = mapped_column(Integer, nullable=False)
    blood_sugar: Mapped[int] = mapped_column(Integer, nullable=False)
    steps: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    sleep_hours: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    memo: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    bmi: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    bmi_category: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    bp_category: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    sugar_category: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    warnings: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True,
    )


class ActivityRecordDB(Base):
    __tablename__ = "activity_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    measured_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    heart_rate: Mapped[float] = mapped_column(Float, nullable=False)
    steps: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    active_energy: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )
    workout_type: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
    )
