import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from backend.app.core.database import Base

class ResolutionRecord(Base):
    __tablename__ = "resolution_records"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    issue_id = Column(String(36), ForeignKey("issues.id", ondelete="CASCADE"), index=True, nullable=False)
    resolved_by_user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    
    resolution_notes = Column(Text, nullable=False)
    proof_image_url = Column(String(500), nullable=True)
    resolved_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Human Verification
    is_verified = Column(Boolean, default=False, nullable=False)
    verified_by_user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    verification_notes = Column(Text, nullable=True)
    verified_at = Column(DateTime, nullable=True)

    issue = relationship("Issue", back_populates="resolution_records")
    resolved_by = relationship("User", foreign_keys=[resolved_by_user_id])
    verified_by = relationship("User", foreign_keys=[verified_by_user_id])
