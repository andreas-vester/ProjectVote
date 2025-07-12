import enum
import uuid
from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Enum as PyEnum,
    ForeignKey,
)
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()


class ApplicationStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class VoteOption(str, enum.Enum):
    APPROVE = "approve"
    REJECT = "reject"
    ABSTAIN = "abstain"


class VoteStatus(str, enum.Enum):
    PENDING = "pending"
    CAST = "cast"


class Application(Base):
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


def generate_uuid():
    return str(uuid.uuid4())


class VoteRecord(Base):
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
