from typing import List, Dict, Any, Optional
import numpy as np
from sqlalchemy.orm import Session
from sklearn.cluster import DBSCAN

from backend.app.models.issue import Issue, IssueStatus
from backend.app.models.report import Report
from backend.app.utils.geo import haversine_distance_meters

class GeospatialService:
    def get_map_issues(
        self,
        db: Session,
        min_lat: Optional[float] = None,
        max_lat: Optional[float] = None,
        min_lng: Optional[float] = None,
        max_lng: Optional[float] = None,
        category_code: Optional[str] = None,
        status: Optional[str] = None,
        priority_band: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        query = db.query(Issue)

        if category_code:
            query = query.join(Issue.category).filter(Issue.category.has(code=category_code))
        if status:
            query = query.filter(Issue.status == status)
        if priority_band:
            query = query.filter(Issue.priority_band == priority_band)

        issues = query.all()
        results = []

        for issue in issues:
            # Viewport bounding box filter if provided
            if min_lat is not None and not (min_lat <= issue.latitude <= max_lat):
                continue
            if min_lng is not None and not (min_lng <= issue.longitude <= max_lng):
                continue

            first_rep = db.query(Report).filter(Report.issue_id == issue.id).first()
            img_url = first_rep.image_url if first_rep else None

            results.append({
                "id": issue.id,
                "issue_code": issue.issue_code,
                "title": issue.title,
                "category_code": issue.category.code if issue.category else "other",
                "category_name": issue.category.display_name if issue.category else "Civic Issue",
                "status": issue.status,
                "latitude": issue.latitude,
                "longitude": issue.longitude,
                "priority_score": issue.priority_score,
                "priority_band": issue.priority_band,
                "report_count": issue.report_count,
                "image_url": img_url,
                "created_at": issue.created_at.strftime("%Y-%m-%d %H:%M")
            })

        return results

    def get_heatmap_points(self, db: Session) -> List[Dict[str, float]]:
        """Returns coordinate points weighted by priority and recurrence."""
        issues = db.query(Issue).filter(Issue.status != IssueStatus.RESOLVED).all()
        points = []
        for issue in issues:
            # Normalized intensity 0.2 to 1.0
            weight = max(0.2, min(1.0, (issue.priority_score / 100.0) * (1.0 + issue.report_count * 0.15)))
            points.append({
                "lat": issue.latitude,
                "lng": issue.longitude,
                "intensity": round(weight, 3)
            })
        return points

    def get_hotspot_clusters(self, db: Session, eps_meters: float = 350.0, min_samples: int = 2) -> List[Dict[str, Any]]:
        """
        Uses DBSCAN density-based spatial clustering to discover recurrence hotspots.
        eps_meters ~ 350m neighborhood radius.
        """
        issues = db.query(Issue).filter(Issue.status != IssueStatus.RESOLVED).all()
        if len(issues) < min_samples:
            return []

        # Convert lat/lng to radians for haversine metric
        coords = np.array([[issue.latitude, issue.longitude] for issue in issues])
        kms_per_radian = 6371.0088
        epsilon_radians = (eps_meters / 1000.0) / kms_per_radian

        dbscan = DBSCAN(eps=epsilon_radians, min_samples=min_samples, metric='haversine')
        rad_coords = np.radians(coords)
        cluster_labels = dbscan.fit_predict(rad_coords)

        clusters = []
        unique_labels = set(cluster_labels)

        for label in unique_labels:
            if label == -1:
                # Noise points
                continue
            
            cluster_indices = np.where(cluster_labels == label)[0]
            cluster_issues = [issues[idx] for idx in cluster_indices]

            center_lat = float(np.mean([i.latitude for i in cluster_issues]))
            center_lng = float(np.mean([i.longitude for i in cluster_issues]))
            
            # Find max radius within cluster
            max_r = 0.0
            for i in cluster_issues:
                d = haversine_distance_meters(center_lat, center_lng, i.latitude, i.longitude)
                if d > max_r:
                    max_r = d

            avg_prio = float(np.mean([i.priority_score for i in cluster_issues]))
            
            # Dominant category
            cat_counts = {}
            for i in cluster_issues:
                cname = i.category.display_name if i.category else "Other"
                cat_counts[cname] = cat_counts.get(cname, 0) + 1
            dom_cat = max(cat_counts.items(), key=lambda x: x[1])[0]

            severity = "SEVERE" if avg_prio >= 75 or len(cluster_issues) >= 5 else ("HIGH" if avg_prio >= 60 else "MODERATE")

            clusters.append({
                "cluster_id": int(label),
                "center_lat": round(center_lat, 6),
                "center_lng": round(center_lng, 6),
                "radius_meters": max(60.0, round(max_r, 1)),
                "issue_count": len(cluster_issues),
                "dominant_category": dom_cat,
                "average_priority": round(avg_prio, 1),
                "severity_level": severity
            })

        return clusters

geospatial_service = GeospatialService()
