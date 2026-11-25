from typing import List, Dict, Any
from pydantic import BaseModel

class AnalyticsSummary(BaseModel):
    total_issues: int
    pending_issues: int
    verified_issues: int
    in_progress_issues: int
    resolved_issues: int
    duplicate_reports_identified: int
    average_resolution_hours: float
    high_critical_count: int

class CategoryCount(BaseModel):
    category_code: str
    category_name: str
    count: int
    percentage: float

class WardCount(BaseModel):
    ward_name: str
    count: int
    unresolved_count: int

class PriorityBandCount(BaseModel):
    band: str
    count: int
    percentage: float

class DailyTrend(BaseModel):
    date: str
    reported: int
    resolved: int
