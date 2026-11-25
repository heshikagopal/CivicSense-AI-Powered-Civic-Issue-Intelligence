import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from backend.app.core.database import Base

class IssueCategory(Base):
    __tablename__ = "issue_categories"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    code = Column(String(60), unique=True, index=True, nullable=False)
    display_name = Column(String(120), nullable=False)
    description = Column(Text, nullable=True)
    default_department_id = Column(String(36), ForeignKey("departments.id", ondelete="SET NULL"), nullable=True)
    base_risk_score = Column(Float, default=50.0, nullable=False)  # 0 to 100
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    default_department = relationship("Department", back_populates="categories")
    issues = relationship("Issue", back_populates="category")
