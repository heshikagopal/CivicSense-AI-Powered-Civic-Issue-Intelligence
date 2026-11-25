from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.models.user import User
from backend.app.models.issue import Issue, IssueStatus
from backend.app.models.report import Report
from backend.app.models.detection import DetectedObject
from backend.app.models.assignment import DepartmentAssignment
from backend.app.models.resolution import ResolutionRecord
from backend.app.models.audit import AuditLog
from backend.app.schemas.issue import IssueResponse, IssueDetail, IssueStatusUpdate
from backend.app.schemas.report import ReportResponse
from backend.app.api.deps import get_current_active_officer
from backend.app.services.audit_service import audit_service
from backend.app.services.priority_service import priority_service

router = APIRouter(tags=["Issue Management"])

@router.get("/issues", response_model=List[IssueResponse])
def list_issues(
    category: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    ward_id: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db)
):
    query = db.query(Issue)
    if category:
        query = query.join(Issue.category).filter(Issue.category.has(code=category))
    if status:
        query = query.filter(Issue.status == status)
    if priority:
        query = query.filter(Issue.priority_band == priority)
    if ward_id:
        query = query.filter(Issue.ward_id == ward_id)

    issues = query.order_by(Issue.priority_score.desc(), Issue.created_at.desc()).offset(skip).limit(limit).all()
    
    results = []
    for i in issues:
        resp = IssueResponse(
            id=i.id,
            issue_code=i.issue_code,
            category_id=i.category_id,
            category_code=i.category.code if i.category else None,
            category_name=i.category.display_name if i.category else None,
            ward_id=i.ward_id,
            ward_name=i.ward.name if i.ward else None,
            title=i.title,
            description=i.description,
            status=i.status,
            latitude=i.latitude,
            longitude=i.longitude,
            address=i.address,
            priority_score=i.priority_score,
            priority_band=i.priority_band,
            report_count=i.report_count,
            assigned_department_id=i.assigned_department_id,
            assigned_department_name=i.assigned_department_id and i.category and i.category.default_department and i.category.default_department.name,
            assigned_officer_id=i.assigned_officer_id,
            first_reported_at=i.first_reported_at,
            last_reported_at=i.last_reported_at,
            resolved_at=i.resolved_at,
            verified_at=i.verified_at,
            created_at=i.created_at
        )
        results.append(resp)
    return results

@router.get("/issues/{issue_id}", response_model=IssueDetail)
def get_issue_detail(issue_id: str, db: Session = Depends(get_db)):
    issue = db.query(Issue).filter(Issue.id == issue_id).first()
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found.")

    # Reports
    reports = db.query(Report).filter(Report.issue_id == issue.id).order_by(Report.created_at.desc()).all()
    rep_responses = [ReportResponse.model_validate(r) for r in reports]

    # Detections across reports
    detections = []
    for r in reports:
        for d in r.detections:
            detections.append({
                "category_code": d.category_code,
                "confidence": d.confidence,
                "bbox": [d.bbox_x1, d.bbox_y1, d.bbox_x2, d.bbox_y2],
                "model_version": d.model_version,
                "created_at": d.created_at.strftime("%Y-%m-%d %H:%M")
            })

    # Assignments
    assignments = []
    for a in issue.assignments:
        assignments.append({
            "id": a.id,
            "department_name": a.department.name if a.department else "Dept",
            "assigned_to_name": a.assigned_to.full_name if a.assigned_to else "Unassigned",
            "status": a.status,
            "notes": a.notes,
            "assigned_at": a.assigned_at.strftime("%Y-%m-%d %H:%M")
        })

    # Resolutions
    resolutions = []
    for res in issue.resolution_records:
        resolutions.append({
            "id": res.id,
            "resolved_by_name": res.resolved_by.full_name if res.resolved_by else "Field Team",
            "notes": res.resolution_notes,
            "proof_image_url": res.proof_image_url,
            "is_verified": res.is_verified,
            "verified_by_name": res.verified_by.full_name if res.verified_by else None,
            "verification_notes": res.verification_notes,
            "resolved_at": res.resolved_at.strftime("%Y-%m-%d %H:%M")
        })

    return {
        "id": issue.id,
        "issue_code": issue.issue_code,
        "category_id": issue.category_id,
        "category_code": issue.category.code if issue.category else None,
        "category_name": issue.category.display_name if issue.category else None,
        "ward_id": issue.ward_id,
        "ward_name": issue.ward.name if issue.ward else None,
        "title": issue.title,
        "description": issue.description,
        "status": issue.status,
        "latitude": issue.latitude,
        "longitude": issue.longitude,
        "address": issue.address,
        "priority_score": issue.priority_score,
        "priority_band": issue.priority_band,
        "report_count": issue.report_count,
        "assigned_department_id": issue.assigned_department_id,
        "assigned_department_name": issue.category and issue.category.default_department and issue.category.default_department.name,
        "assigned_officer_id": issue.assigned_officer_id,
        "first_reported_at": issue.first_reported_at,
        "last_reported_at": issue.last_reported_at,
        "resolved_at": issue.resolved_at,
        "verified_at": issue.verified_at,
        "created_at": issue.created_at,
        "reports": rep_responses,
        "recent_detections": detections,
        "assignments": assignments,
        "resolutions": resolutions
    }

@router.patch("/issues/{issue_id}/status")
def update_issue_status(
    issue_id: str,
    status_in: IssueStatusUpdate,
    db: Session = Depends(get_db),
    current_officer: User = Depends(get_current_active_officer)
):
    issue = db.query(Issue).filter(Issue.id == issue_id).first()
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found.")

    old_status = issue.status
    issue.status = status_in.status

    audit_service.log_action(
        db=db,
        user_id=current_officer.id,
        action="ISSUE_STATUS_UPDATE",
        entity_type="ISSUE",
        entity_id=issue.id,
        details={"old_status": old_status, "new_status": status_in.status, "notes": status_in.notes}
    )

    db.commit()
    return {"message": "Status updated successfully.", "status": issue.status}

@router.get("/issues/{issue_id}/audit")
def get_issue_audit(issue_id: str, db: Session = Depends(get_db)):
    logs = db.query(AuditLog).filter(
        (AuditLog.entity_id == issue_id) | (AuditLog.entity_type == "ISSUE")
    ).order_by(AuditLog.timestamp.desc()).limit(20).all()
    
    return [
        {
            "id": l.id,
            "action": l.action,
            "entity_type": l.entity_type,
            "user_name": l.user.full_name if l.user else "System",
            "details": l.details_json,
            "timestamp": l.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        }
        for l in logs
    ]
