import uuid
from datetime import datetime
from enum import Enum
from sqlalchemy import Column, String, Text, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from backend.app.core.database import Base

class ReportStatus(str, Enum):
    SUBMITTED = "SUBMITTED"
    LINKED_TO_ISSUE = "LINKED_TO_ISSUE"
    REJECTED = "REJECTED"

class Report(Base):
    __tablename__ = "reports"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    report_code = Column(String(50), unique=True, index=True, nullable=False)
    issue_id = Column(String(36), ForeignKey("issues.id", ondelete="SET NULL"), index=True, nullable=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), index=True, nullable=True)
    
    user_latitude = Column(Float, nullable=False)
    user_longitude = Column(Float, nullable=False)
    address_text = Column(String(500), nullable=True)
    
    image_url = Column(String(500), nullable=False)
    image_hash = Column(String(64), index=True, nullable=True)
    
    citizen_category_suggestion = Column(String(100), nullable=True)
    citizen_comment = Column(Text, nullable=True)
    consent_given = Column(Boolean, default=True, nullable=False)
    
    status = Column(String(50), default=ReportStatus.SUBMITTED, index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="reports")
    issue = relationship("Issue", back_populates="reports")
    metadata_entry = relationship("ImageMetadata", back_populates="report", uselist=False)
    detections = relationship("DetectedObject", back_populates="report")
    duplicate_matches = relationship("DuplicateMatch", back_populates="report")
