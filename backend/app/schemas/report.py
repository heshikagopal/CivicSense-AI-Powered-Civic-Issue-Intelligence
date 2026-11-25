from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel

class ReportCreate(BaseModel):
    latitude: float
    longitude: float
    address_text: Optional[str] = None
    image_url: str
    citizen_category_suggestion: Optional[str] = None
    citizen_comment: Optional[str] = None
    consent_given: bool = True
    # Optional bounding boxes if citizen confirmed detection
    confirmed_category_code: Optional[str] = None

class ReportResponse(BaseModel):
    id: str
    report_code: str
    issue_id: Optional[str] = None
    user_id: Optional[str] = None
    user_latitude: float
    user_longitude: float
    address_text: Optional[str] = None
    image_url: str
    citizen_category_suggestion: Optional[str] = None
    citizen_comment: Optional[str] = None
    status: str
    created_at: datetime

    class Config:
        from_attributes = True
