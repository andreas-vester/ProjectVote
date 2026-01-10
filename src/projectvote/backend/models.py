"""SQLAlchemy models for the application."""

import datetime as dt
import enum
import uuid

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String
from sqlalchemy import (
    Enum as PyEnum,
)
from sqlalchemy.orm import (
    Mapped,
    declarative_base,
    mapped_column,
    relationship,
)
from sqlalchemy.sql import func

Base = declarative_base()


class ApplicationStatus(str, enum.Enum):
    """Enum for the status of an application."""

    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class VoteOption(str, enum.Enum):
    """Enum for the options a voter can take."""

    APPROVE = "approve"
    REJECT = "reject"
    ABSTAIN = "abstain"


class VoteStatus(str, enum.Enum):
    """Enum for the status of a vote."""

    PENDING = "pending"
    CAST = "cast"


class Application(Base):
    """Represents a funding application."""

    __tablename__ = "applications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    first_name: Mapped[str] = mapped_column(String, nullable=False)
    last_name: Mapped[str] = mapped_column(String, nullable=False)
    applicant_email: Mapped[str] = mapped_column(String, nullable=False)
    department: Mapped[str] = mapped_column(String, nullable=False)
    project_title: Mapped[str] = mapped_column(String, nullable=False)
    project_description: Mapped[str] = mapped_column(String, nullable=False)
    costs: Mapped[float] = mapped_column(Float, nullable=False)
    status: Mapped[ApplicationStatus] = mapped_column(
        PyEnum(ApplicationStatus), default=ApplicationStatus.PENDING, nullable=False
    )
    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    concluded_at: Mapped[dt.datetime | None] = mapped_column(DateTime, nullable=True)

    votes: Mapped[list["VoteRecord"]] = relationship(back_populates="application")
    attachments: Mapped[list["Attachment"]] = relationship(back_populates="application")


def generate_uuid() -> str:
    """Generate a unique UUID for a vote record."""
    return str(uuid.uuid4())


class VoteRecord(Base):
    """Represents a single vote record for an application."""

    __tablename__ = "votes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    application_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("applications.id"), nullable=False
    )
    voter_email: Mapped[str] = mapped_column(String, nullable=False)
    token: Mapped[str] = mapped_column(
        String, unique=True, index=True, nullable=False, default=generate_uuid
    )
    vote: Mapped[VoteOption | None] = mapped_column(PyEnum(VoteOption), nullable=True)
    vote_status: Mapped[VoteStatus] = mapped_column(
        PyEnum(VoteStatus), default=VoteStatus.PENDING, nullable=False
    )
    voted_at: Mapped[dt.datetime | None] = mapped_column(DateTime, nullable=True)

    application: Mapped["Application"] = relationship(back_populates="votes")


class Attachment(Base):
    """Represents an uploaded file attachment for an application."""

    __tablename__ = "attachments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    application_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("applications.id"), nullable=False
    )
    filename: Mapped[str] = mapped_column(String, nullable=False)
    filepath: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    mime_type: Mapped[str] = mapped_column(String, nullable=False)

    application: Mapped["Application"] = relationship(back_populates="attachments")
