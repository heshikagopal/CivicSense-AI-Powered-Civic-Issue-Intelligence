from typing import Optional
from datetime import datetime
from pydantic import BaseModel

class ResolutionCreate(BaseModel):
    resolution_notes: str
    proof_image_url: Optional[str] = None

class ResolutionVerifyRequest(BaseModel):
    is_verified: bool
    verification_notes: Optional[str] = None

class ResolutionResponse(BaseModel):
    id: str
    issue_id: str
    resolved_by_user_id: Optional[str] = None
    resolved_by_name: Optional[str] = None
    resolution_notes: str
    proof_image_url: Optional[str] = None
    is_verified: bool
    verified_by_user_id: Optional[str] = None
    verification_notes: Optional[str] = None
    resolved_at: datetime
    verified_at: Optional[datetime] = None

    class Config:
        from_attributes = True
