from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.schemas.map import MapIssuePoint, MapHeatmapPoint, HotspotCluster
from backend.app.services.geospatial_service import geospatial_service

router = APIRouter(tags=["Map & Geospatial Intelligence"])

@router.get("/map/issues", response_model=List[MapIssuePoint])
def get_map_issues(
    min_lat: Optional[float] = Query(None),
    max_lat: Optional[float] = Query(None),
    min_lng: Optional[float] = Query(None),
    max_lng: Optional[float] = Query(None),
    category: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Returns geo-located civic issues with optional bounding box and attribute filtering.
    """
    return geospatial_service.get_map_issues(
        db=db,
        min_lat=min_lat,
        max_lat=max_lat,
        min_lng=min_lng,
        max_lng=max_lng,
        category_code=category,
        status=status,
        priority_band=priority
    )

@router.get("/map/heatmap", response_model=List[MapHeatmapPoint])
def get_heatmap(db: Session = Depends(get_db)):
    """
    Returns weighted coordinate intensities for urban civic density heatmaps.
    """
    return geospatial_service.get_heatmap_points(db)

@router.get("/map/hotspots", response_model=List[HotspotCluster])
def get_hotspots(
    eps_meters: float = Query(350.0, description="DBSCAN clustering radius in meters"),
    min_samples: int = Query(2, description="Minimum issues per recurrence cluster"),
    db: Session = Depends(get_db)
):
    """
    Discovers recurrence hotspots using DBSCAN spatial density clustering.
    """
    return geospatial_service.get_hotspot_clusters(db, eps_meters=eps_meters, min_samples=min_samples)
