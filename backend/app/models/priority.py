import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, Boolean, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from backend.app.core.database import Base

class IssuePriority(Base):
    __tablename__ = "issue_priorities"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    issue_id = Column(String(36), ForeignKey("issues.id", ondelete="CASCADE"), unique=True, nullable=False)
    
    # 5 Explainable Factors
    base_risk_score = Column(Float, nullable=False)           # 25%
    damage_extent_score = Column(Float, nullable=False)       # 20%
    location_context_score = Column(Float, nullable=False)    # 20%
    supporting_reports_score = Column(Float, nullable=False)  # 20%
    evidence_quality_score = Column(Float, nullable=False)    # 10%
    age_sla_bonus = Column(Float, default=0.0, nullable=False)# Optional SLA bonus
    
    calculated_priority_score = Column(Float, nullable=False) # 0 to 100
    priority_band = Column(String(20), nullable=False)        # LOW, MEDIUM, HIGH, CRITICAL
    
    # Administrative Override Audit
    is_overridden = Column(Boolean, default=False, nullable=False)
    overridden_by_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    override_reason = Column(Text, nullable=True)
    override_timestamp = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    issue = relationship("Issue", back_populates="priority_record")
    overridden_by = relationship("User")
