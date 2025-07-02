from sqlalchemy import Column, Integer, String, Float, Enum as PyEnum, ForeignKey, Boolean
from sqlalchemy.orm import relationship, declarative_base
import enum

Base = declarative_base()

class ApplicationStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

class VoteOption(str, enum.Enum):
    APPROVE = "approve"
    REJECT = "reject"
    ABSTAIN = "abstain"

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
    status = Column(PyEnum(ApplicationStatus), default=ApplicationStatus.PENDING, nullable=False)

    votes = relationship("VoteRecord", back_populates="application")


class VoteRecord(Base):
    __tablename__ = "votes"

    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Integer, ForeignKey("applications.id"), nullable=False)
    voter_email = Column(String, nullable=False)
    vote = Column(PyEnum(VoteOption), nullable=False)

    application = relationship("Application", back_populates="votes")
