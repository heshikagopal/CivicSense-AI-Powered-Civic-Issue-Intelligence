from datetime import datetime, timedelta
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.app.core.database import get_db
from backend.app.models.issue import Issue, IssueStatus, PriorityBand
from backend.app.models.report import Report
from backend.app.models.category import IssueCategory
from backend.app.models.ward import Ward
from backend.app.models.duplicate import DuplicateMatch, DuplicateReviewStatus
from backend.app.schemas.analytics import AnalyticsSummary, CategoryCount, WardCount, PriorityBandCount, DailyTrend

router = APIRouter(tags=["Data Analytics & Reporting"])

@router.get("/analytics/summary", response_model=AnalyticsSummary)
def get_analytics_summary(db: Session = Depends(get_db)):
    total = db.query(Issue).count()
    pending = db.query(Issue).filter(Issue.status == IssueStatus.REPORTED).count()
    verified = db.query(Issue).filter(Issue.status == IssueStatus.VERIFIED).count()
    in_progress = db.query(Issue).filter(Issue.status == IssueStatus.IN_PROGRESS).count()
    resolved = db.query(Issue).filter(Issue.status == IssueStatus.RESOLVED).count()
    
    dup_count = db.query(DuplicateMatch).filter(
        DuplicateMatch.review_status.in_([DuplicateReviewStatus.AUTO_LINKED, DuplicateReviewStatus.CONFIRMED])
    ).count()

    high_crit = db.query(Issue).filter(
        Issue.priority_band.in_([PriorityBand.HIGH, PriorityBand.CRITICAL])
    ).count()

    # Calculate average resolution hours for resolved issues
    resolved_issues = db.query(Issue).filter(Issue.status == IssueStatus.RESOLVED, Issue.resolved_at.isnot(None)).all()
    avg_hours = 0.0
    if resolved_issues:
        total_hours = sum((i.resolved_at - i.created_at).total_seconds() / 3600.0 for i in resolved_issues)
        avg_hours = round(total_hours / len(resolved_issues), 1)

    return {
        "total_issues": total,
        "pending_issues": pending,
        "verified_issues": verified,
        "in_progress_issues": in_progress,
        "resolved_issues": resolved,
        "duplicate_reports_identified": dup_count,
        "average_resolution_hours": avg_hours,
        "high_critical_count": high_crit
    }

@router.get("/analytics/distribution")
def get_analytics_distribution(db: Session = Depends(get_db)):
    total = max(1, db.query(Issue).count())

    # Category Breakdown
    cat_counts = []
    categories = db.query(IssueCategory).all()
    for c in categories:
        cnt = db.query(Issue).filter(Issue.category_id == c.id).count()
        cat_counts.append({
            "category_code": c.code,
            "category_name": c.display_name,
            "count": cnt,
            "percentage": round((cnt / total) * 100, 1)
        })

    # Priority Bands
    priority_counts = []
    for band in [PriorityBand.LOW, PriorityBand.MEDIUM, PriorityBand.HIGH, PriorityBand.CRITICAL]:
        cnt = db.query(Issue).filter(Issue.priority_band == band).count()
        priority_counts.append({
            "band": band,
            "count": cnt,
            "percentage": round((cnt / total) * 100, 1)
        })

    # Ward Statistics
    ward_counts = []
    wards = db.query(Ward).all()
    for w in wards:
        cnt = db.query(Issue).filter(Issue.ward_id == w.id).count()
        unres = db.query(Issue).filter(Issue.ward_id == w.id, Issue.status != IssueStatus.RESOLVED).count()
        ward_counts.append({
            "ward_name": w.name,
            "count": cnt,
            "unresolved_count": unres
        })

    return {
        "categories": cat_counts,
        "priority_bands": priority_counts,
        "wards": ward_counts
    }

@router.get("/analytics/trends", response_model=List[DailyTrend])
def get_analytics_trends(days: int = 7, db: Session = Depends(get_db)):
    trends = []
    now = datetime.utcnow().date()
    for d in range(days - 1, -1, -1):
        target_date = now - timedelta(days=d)
        start_dt = datetime.combine(target_date, datetime.min.time())
        end_dt = datetime.combine(target_date, datetime.max.time())

        rep_count = db.query(Issue).filter(Issue.created_at.between(start_dt, end_dt)).count()
        res_count = db.query(Issue).filter(Issue.resolved_at.between(start_dt, end_dt)).count()

        trends.append({
            "date": target_date.strftime("%b %d"),
            "reported": rep_count,
            "resolved": res_count
        })
    return trends
