from typing import List, Optional
from pydantic import BaseModel

class DetectionBox(BaseModel):
    category_code: str
    category_name: str
    confidence: float
    bbox: List[float]  # [x1, y1, x2, y2]
    status: str  # HIGH, MEDIUM, LOW

class DetectionResult(BaseModel):
    detections: List[DetectionBox]
    model_version: str
    inference_ms: float
    preview_url: Optional[str] = None
    suggested_category: Optional[str] = None
    confidence_tier: str  # HIGH, MEDIUM, LOW
    is_civic_defect_detected: bool = False
    detection_notes: Optional[str] = None

class ImageUploadResponse(BaseModel):
    image_url: str
    original_filename: str
    file_size_bytes: int
    mime_type: str
