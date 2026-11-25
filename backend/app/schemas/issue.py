from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel
from backend.app.schemas.report import ReportResponse

class PriorityFactorScore(BaseModel):
    score: float
    weight_percent: float
    weighted_contribution: float
    description: str

class PriorityBreakdown(BaseModel):
    issue_id: str
    overall_score: float
    priority_band: str
    is_overridden: bool = False
    override_reason: Optional[str] = None
    factors: Dict[str, PriorityFactorScore]

class PriorityOverrideRequest(BaseModel):
    new_priority_score: float
    override_reason: str

class IssueAssignRequest(BaseModel):
    department_id: str
    officer_id: Optional[str] = None
    notes: Optional[str] = None

class IssueStatusUpdate(BaseModel):
    status: str
    notes: Optional[str] = None

class IssueResponse(BaseModel):
    id: str
    issue_code: str
    category_id: str
    category_code: Optional[str] = None
    category_name: Optional[str] = None
    ward_id: Optional[str] = None
    ward_name: Optional[str] = None
    title: str
    description: Optional[str] = None
    status: str
    latitude: float
    longitude: float
    address: Optional[str] = None
    priority_score: float
    priority_band: str
    report_count: int
    assigned_department_id: Optional[str] = None
    assigned_department_name: Optional[str] = None
    assigned_officer_id: Optional[str] = None
    assigned_officer_name: Optional[str] = None
    first_reported_at: datetime
    last_reported_at: datetime
    resolved_at: Optional[datetime] = None
    verified_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True

class IssueDetail(IssueResponse):
    reports: List[ReportResponse] = []
    priority_details: Optional[PriorityBreakdown] = None
    recent_detections: List[Dict[str, Any]] = []
    assignments: List[Dict[str, Any]] = []
    resolutions: List[Dict[str, Any]] = []
