import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime
from sqlalchemy.orm import relationship
from backend.app.core.database import Base

class Department(Base):
    __tablename__ = "departments"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(120), unique=True, nullable=False)
    code = Column(String(50), unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)
    contact_email = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    staff = relationship("User", back_populates="department")
    categories = relationship("IssueCategory", back_populates="default_department")
    assignments = relationship("DepartmentAssignment", back_populates="department")
