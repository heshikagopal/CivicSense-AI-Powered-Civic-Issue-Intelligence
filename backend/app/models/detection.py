import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, Boolean, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from backend.app.core.database import Base

class ImageMetadata(Base):
    __tablename__ = "image_metadata"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    report_id = Column(String(36), ForeignKey("reports.id", ondelete="CASCADE"), unique=True, nullable=False)
    
    original_filename = Column(String(255), nullable=False)
    stored_filename = Column(String(255), nullable=False)
    file_size_bytes = Column(Integer, nullable=False)
    mime_type = Column(String(100), nullable=False)
    width = Column(Integer, nullable=True)
    height = Column(Integer, nullable=True)
    embedding_json = Column(Text, nullable=True)  # JSON-serialized embedding array for vector similarity
    exif_stripped = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    report = relationship("Report", back_populates="metadata_entry")

class DetectedObject(Base):
    __tablename__ = "detected_objects"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    report_id = Column(String(36), ForeignKey("reports.id", ondelete="CASCADE"), index=True, nullable=False)
    
    category_code = Column(String(60), index=True, nullable=False)
    confidence = Column(Float, nullable=False)
    bbox_x1 = Column(Float, nullable=False)  # Normalized 0.0 - 1.0 or pixel coordinates
    bbox_y1 = Column(Float, nullable=False)
    bbox_x2 = Column(Float, nullable=False)
    bbox_y2 = Column(Float, nullable=False)
    model_version = Column(String(50), default="yolo11-civic-v1.0", nullable=False)
    inference_ms = Column(Float, default=0.0, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    report = relationship("Report", back_populates="detections")
