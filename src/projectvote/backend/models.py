"""SQLAlchemy models for the application."""

import enum
import uuid

from sqlalchemy import (
    Column,
    Float,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy import (
    Enum as PyEnum,
)
from sqlalchemy.orm import declarative_base, relationship

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

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    applicant_email = Column(String, nullable=False)
    department = Column(String, nullable=False)
    project_title = Column(String, nullable=False)
    project_description = Column(String, nullable=False)
    costs = Column(Float, nullable=False)
    status = Column(
        PyEnum(ApplicationStatus), default=ApplicationStatus.PENDING, nullable=False
    )

    votes = relationship("VoteRecord", back_populates="application")
    attachments = relationship("Attachment", back_populates="application")


def generate_uuid() -> str:
    """Generate a unique UUID for a vote record."""
    return str(uuid.uuid4())


class VoteRecord(Base):
    """Represents a single vote record for an application."""

    __tablename__ = "votes"

    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Integer, ForeignKey("applications.id"), nullable=False)
    voter_email = Column(String, nullable=False)
    token = Column(
        String, unique=True, index=True, nullable=False, default=generate_uuid
    )
    vote = Column(PyEnum(VoteOption), nullable=True)
    vote_status = Column(PyEnum(VoteStatus), default=VoteStatus.PENDING, nullable=False)

    application = relationship("Application", back_populates="votes")


class Attachment(Base):
    """Represents an uploaded file attachment for an application."""

    __tablename__ = "attachments"

    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Integer, ForeignKey("applications.id"), nullable=False)
    filename = Column(String, nullable=False)
    filepath = Column(String, nullable=False, unique=True)
    mime_type = Column(String, nullable=False)

    application = relationship("Application", back_populates="attachments")
