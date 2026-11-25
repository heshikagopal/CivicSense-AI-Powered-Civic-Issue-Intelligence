import json
from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session

from backend.app.core.config import settings
from backend.app.models.issue import Issue, IssueStatus
from backend.app.models.report import Report
from backend.app.models.detection import ImageMetadata
from backend.app.models.category import IssueCategory
from backend.app.utils.geo import haversine_distance_meters, compute_spatial_similarity, compute_temporal_similarity
from backend.app.services.embedding_service import embedding_service

class DuplicateService:
    def evaluate_duplicate_candidates(
        self,
        db: Session,
        latitude: float,
        longitude: float,
        category_code: Optional[str] = None,
        image_embedding: Optional[List[float]] = None,
        exclude_issue_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Finds nearby potential duplicate issues and calculates combined
        visual, spatial, and temporal similarity scores.
        """
        # 1. Query active / unresolved issues
        query = db.query(Issue).filter(
            Issue.status.in_([IssueStatus.REPORTED, IssueStatus.VERIFIED, IssueStatus.IN_PROGRESS])
        )
        if exclude_issue_id:
            query = query.filter(Issue.id != exclude_issue_id)
            
        all_active_issues = query.all()
        candidates = []
        radius_limit = settings.DUPLICATE_SEARCH_RADIUS_METERS

        now = datetime.utcnow()

        for issue in all_active_issues:
            dist_m = haversine_distance_meters(latitude, longitude, issue.latitude, issue.longitude)
            if dist_m > radius_limit:
                continue

            # 2. Geospatial Similarity
            spatial_sim = compute_spatial_similarity(dist_m, radius_limit)

            # 3. Temporal Similarity (hours since last report)
            time_diff = abs((now - issue.last_reported_at).total_seconds() / 3600.0)
            temporal_sim = compute_temporal_similarity(time_diff)

            # 4. Visual Similarity
            visual_sim = 0.5  # Neutral baseline if images unavailable
            category_match_bonus = 0.0

            if category_code and issue.category and issue.category.code == category_code:
                category_match_bonus = 0.10

            # Check embeddings from reports associated with this candidate issue
            if image_embedding:
                best_img_sim = 0.0
                issue_reports = db.query(Report).filter(Report.issue_id == issue.id).all()
                for rep in issue_reports:
                    if rep.metadata_entry and rep.metadata_entry.embedding_json:
                        try:
                            stored_vec = json.loads(rep.metadata_entry.embedding_json)
                            sim = embedding_service.cosine_similarity(image_embedding, stored_vec)
                            if sim > best_img_sim:
                                best_img_sim = sim
                        except Exception:
                            pass
                if best_img_sim > 0.0:
                    visual_sim = best_img_sim

            # 5. Combined Multi-Factor Duplicate Score
            # Weights: Visual 45%, Spatial 40%, Temporal 15%
            overall_score = (visual_sim * 0.45) + (spatial_sim * 0.40) + (temporal_sim * 0.15) + category_match_bonus
            overall_score = max(0.0, min(1.0, round(overall_score, 4)))

            # Recommended Action Tier
            if overall_score >= settings.DUPLICATE_AUTO_MERGE_THRESHOLD:
                action = "AUTO_LINK"
            elif overall_score >= settings.DUPLICATE_MANUAL_REVIEW_THRESHOLD:
                action = "MANUAL_REVIEW"
            else:
                action = "NEW_ISSUE"

            # Primary image for UI preview
            primary_image = None
            first_report = db.query(Report).filter(Report.issue_id == issue.id).first()
            if first_report:
                primary_image = first_report.image_url

            candidates.append({
                "candidate_issue_id": issue.id,
                "issue_code": issue.issue_code,
                "category_name": issue.category.display_name if issue.category else "Civic Issue",
                "status": issue.status,
                "latitude": issue.latitude,
                "longitude": issue.longitude,
                "address": issue.address,
                "distance_meters": round(dist_m, 1),
                "time_difference_hours": round(time_diff, 1),
                "visual_similarity": round(visual_sim, 3),
                "overall_duplicate_score": overall_score,
                "recommended_action": action,
                "primary_image_url": primary_image
            })

        # Rank candidates by overall similarity score descending
        candidates.sort(key=lambda c: c["overall_duplicate_score"], reverse=True)
        return candidates

duplicate_service = DuplicateService()
