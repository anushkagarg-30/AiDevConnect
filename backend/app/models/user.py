from __future__ import annotations

import enum
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.match_request import MatchRequest
    from app.models.project import Project


class UserRole(str, enum.Enum):
    USER = "user"
    ADMIN = "admin"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    username: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, name="userrole", values_callable=lambda obj: [e.value for e in obj]),
        default=UserRole.USER,
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    projects: Mapped[list[Project]] = relationship(back_populates="owner", cascade="all, delete-orphan")
    sent_match_requests: Mapped[list[MatchRequest]] = relationship(
        back_populates="requester",
        foreign_keys="MatchRequest.requester_id",
        cascade="all, delete-orphan",
    )
    received_match_requests: Mapped[list[MatchRequest]] = relationship(
        back_populates="recipient",
        foreign_keys="MatchRequest.recipient_id",
        cascade="all, delete-orphan",
    )
