import uuid
from datetime import datetime
from enum import Enum
from sqlalchemy import Column, String, Text, Float, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from backend.app.core.database import Base

class IssueStatus(str, Enum):
    REPORTED = "REPORTED"
    VERIFIED = "VERIFIED"
    IN_PROGRESS = "IN_PROGRESS"
    RESOLVED = "RESOLVED"
    REJECTED = "REJECTED"

class PriorityBand(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class Issue(Base):
    __tablename__ = "issues"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    issue_code = Column(String(50), unique=True, index=True, nullable=False)
    category_id = Column(String(36), ForeignKey("issue_categories.id"), nullable=False)
    ward_id = Column(String(36), ForeignKey("wards.id", ondelete="SET NULL"), nullable=True)
    
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(50), default=IssueStatus.REPORTED, index=True, nullable=False)
    
    latitude = Column(Float, index=True, nullable=False)
    longitude = Column(Float, index=True, nullable=False)
    address = Column(String(500), nullable=True)
    
    priority_score = Column(Float, default=30.0, index=True, nullable=False)
    priority_band = Column(String(20), default=PriorityBand.LOW, index=True, nullable=False)
    report_count = Column(Integer, default=1, nullable=False)
    
    assigned_department_id = Column(String(36), ForeignKey("departments.id", ondelete="SET NULL"), nullable=True)
    assigned_officer_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    
    first_reported_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_reported_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    resolved_at = Column(DateTime, nullable=True)
    verified_at = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    category = relationship("IssueCategory", back_populates="issues")
    ward = relationship("Ward", back_populates="issues")
    reports = relationship("Report", back_populates="issue")
    priority_record = relationship("IssuePriority", back_populates="issue", uselist=False)
    assignments = relationship("DepartmentAssignment", back_populates="issue")
    resolution_records = relationship("ResolutionRecord", back_populates="issue")
