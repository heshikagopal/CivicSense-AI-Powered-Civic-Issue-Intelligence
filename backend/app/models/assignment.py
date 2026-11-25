import uuid
from datetime import datetime
from enum import Enum
from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from backend.app.core.database import Base

class AssignmentStatus(str, Enum):
    ASSIGNED = "ASSIGNED"
    ACCEPTED = "ACCEPTED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"

class DepartmentAssignment(Base):
    __tablename__ = "department_assignments"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    issue_id = Column(String(36), ForeignKey("issues.id", ondelete="CASCADE"), index=True, nullable=False)
    department_id = Column(String(36), ForeignKey("departments.id", ondelete="CASCADE"), index=True, nullable=False)
    assigned_to_user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    assigned_by_user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    
    status = Column(String(50), default=AssignmentStatus.ASSIGNED, nullable=False)
    notes = Column(Text, nullable=True)
    
    assigned_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)

    issue = relationship("Issue", back_populates="assignments")
    department = relationship("Department", back_populates="assignments")
    assigned_to = relationship("User", foreign_keys=[assigned_to_user_id])
    assigned_by = relationship("User", foreign_keys=[assigned_by_user_id])
