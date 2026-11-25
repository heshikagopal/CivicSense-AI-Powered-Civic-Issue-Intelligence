import uuid
from datetime import datetime
from enum import Enum
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from backend.app.core.database import Base

class UserRole(str, Enum):
    CITIZEN = "citizen"
    OFFICER = "officer"
    ADMIN = "admin"

class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    phone = Column(String(50), nullable=True)
    role = Column(String(50), default=UserRole.CITIZEN, nullable=False)
    department_id = Column(String(36), ForeignKey("departments.id", ondelete="SET NULL"), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    department = relationship("Department", back_populates="staff")
    reports = relationship("Report", back_populates="user")
    notifications = relationship("Notification", back_populates="user")
