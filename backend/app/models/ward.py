import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, Text
from sqlalchemy.orm import relationship
from backend.app.core.database import Base

class Ward(Base):
    __tablename__ = "wards"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    ward_number = Column(Integer, unique=True, index=True, nullable=False)
    name = Column(String(120), nullable=False)
    boundary_geojson = Column(Text, nullable=True)
    population_density_level = Column(String(50), default="MEDIUM") # LOW, MEDIUM, HIGH, CRITICAL
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    issues = relationship("Issue", back_populates="ward")
