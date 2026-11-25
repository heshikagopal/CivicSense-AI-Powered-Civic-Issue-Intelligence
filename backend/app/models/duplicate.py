import uuid
from datetime import datetime
from enum import Enum
from sqlalchemy import Column, String, Float, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from backend.app.core.database import Base

class DuplicateReviewStatus(str, Enum):
    PENDING = "PENDING"
    AUTO_LINKED = "AUTO_LINKED"
    CONFIRMED = "CONFIRMED"
    REJECTED = "REJECTED"

class DuplicateMatch(Base):
    __tablename__ = "duplicate_matches"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    report_id = Column(String(36), ForeignKey("reports.id", ondelete="CASCADE"), index=True, nullable=False)
    candidate_issue_id = Column(String(36), ForeignKey("issues.id", ondelete="CASCADE"), index=True, nullable=False)
    
    visual_similarity = Column(Float, nullable=False)        # 0.0 to 1.0 (cosine similarity)
    geospatial_distance_meters = Column(Float, nullable=False)
    temporal_difference_hours = Column(Float, nullable=False)
    overall_duplicate_score = Column(Float, index=True, nullable=False)  # Weighted combo
    
    review_status = Column(String(50), default=DuplicateReviewStatus.PENDING, index=True, nullable=False)
    reviewed_by_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    review_notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    report = relationship("Report", back_populates="duplicate_matches")
    candidate_issue = relationship("Issue")
    reviewer = relationship("User")
