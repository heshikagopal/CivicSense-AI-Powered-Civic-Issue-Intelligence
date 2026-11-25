import os
import uuid
import shutil
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session

from backend.app.core.config import settings
from backend.app.core.database import get_db
from backend.app.schemas.detection import DetectionResult, ImageUploadResponse
from backend.app.services.detection_service import detection_service
from backend.app.utils.image import strip_exif_and_save

router = APIRouter(tags=["Image Detection & Uploads"])

@router.post("/uploads", response_model=ImageUploadResponse)
async def upload_image(file: UploadFile = File(...)):
    # Validate MIME type
    if file.content_type not in settings.ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file format {file.content_type}. Allowed: {settings.ALLOWED_IMAGE_TYPES}"
        )

    # Generate secure filename
    ext = os.path.splitext(file.filename)[1].lower() or ".jpg"
    safe_name = f"{uuid.uuid4().hex}{ext}"
    temp_path = os.path.join(settings.UPLOAD_DIR, f"raw_{safe_name}")
    final_path = os.path.join(settings.UPLOAD_DIR, safe_name)

    # Save temp file
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Strip EXIF and optimize image for citizen privacy
    try:
        w, h, size_bytes = strip_exif_and_save(temp_path, final_path)
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

    image_url = f"/static/uploads/{safe_name}"
    return {
        "image_url": image_url,
        "original_filename": file.filename,
        "file_size_bytes": size_bytes,
        "mime_type": file.content_type
    }

@router.post("/detect", response_model=DetectionResult)
async def detect_issue(image_url: str = Form(...)):
    """
    Runs YOLO object detection on the uploaded image URL.
    Returns detected categories, confidence scores, bounding boxes, and preview URL.
    """
    # Extract filename from URL
    filename = os.path.basename(image_url)
    image_path = os.path.join(settings.UPLOAD_DIR, filename)

    if not os.path.exists(image_path):
        raise HTTPException(status_code=404, detail="Image file not found on server.")

    result = detection_service.detect(image_path)
    return result
