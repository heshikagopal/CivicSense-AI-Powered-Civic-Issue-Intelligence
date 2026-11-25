from typing import List, Optional, Dict, Any
from pydantic import BaseModel

class MapIssuePoint(BaseModel):
    id: str
    issue_code: str
    title: str
    category_code: str
    category_name: str
    status: str
    latitude: float
    longitude: float
    priority_score: float
    priority_band: str
    report_count: int
    image_url: Optional[str] = None
    created_at: str

class MapHeatmapPoint(BaseModel):
    lat: float
    lng: float
    intensity: float  # Weighted by priority_score and report_count

class HotspotCluster(BaseModel):
    cluster_id: int
    center_lat: float
    center_lng: float
    radius_meters: float
    issue_count: int
    dominant_category: str
    average_priority: float
    severity_level: str  # LOW, MODERATE, HIGH, SEVERE
