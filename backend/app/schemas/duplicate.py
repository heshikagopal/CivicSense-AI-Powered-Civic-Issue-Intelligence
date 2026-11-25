from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel

class DuplicateCandidate(BaseModel):
    match_id: Optional[str] = None
    candidate_issue_id: str
    issue_code: str
    category_name: str
    status: str
    latitude: float
    longitude: float
    address: Optional[str] = None
    distance_meters: float
    time_difference_hours: float
    visual_similarity: float
    overall_duplicate_score: float
    recommended_action: str  # AUTO_LINK, MANUAL_REVIEW, NEW_ISSUE
    primary_image_url: Optional[str] = None

class DuplicateCheckRequest(BaseModel):
    latitude: float
    longitude: float
    category_code: Optional[str] = None
    image_url: Optional[str] = None

class DuplicateReviewRequest(BaseModel):
    decision: str  # CONFIRM_DUPLICATE, REJECT_DUPLICATE
    review_notes: Optional[str] = None
