import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.models.user import User, UserRole
from backend.app.models.issue import Issue, IssueStatus
from backend.app.models.report import Report
from backend.app.models.resolution import ResolutionRecord
from backend.app.schemas.resolution import ResolutionCreate, ResolutionVerifyRequest, ResolutionResponse
from backend.app.api.deps import get_current_active_officer, get_current_active_admin
from backend.app.services.audit_service import audit_service
from backend.app.services.notification_service import notification_service

router = APIRouter(tags=["Resolution & Verification"])

@router.post("/issues/{issue_id}/resolution", response_model=ResolutionResponse)
def submit_resolution(
    issue_id: str,
    res_in: ResolutionCreate,
    db: Session = Depends(get_db),
    current_officer: User = Depends(get_current_active_officer)
):
    issue = db.query(Issue).filter(Issue.id == issue_id).first()
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found.")

    resolution = ResolutionRecord(
        id=str(uuid.uuid4()),
        issue_id=issue.id,
        resolved_by_user_id=current_officer.id,
        resolution_notes=res_in.resolution_notes,
        proof_image_url=res_in.proof_image_url,
        resolved_at=datetime.utcnow(),
        is_verified=False
    )
    db.add(resolution)

    issue.status = IssueStatus.RESOLVED
    issue.resolved_at = datetime.utcnow()

    audit_service.log_action(
        db=db,
        user_id=current_officer.id,
        action="RESOLUTION_SUBMITTED",
        entity_type="ISSUE",
        entity_id=issue.id,
        details={"notes": res_in.resolution_notes, "proof": res_in.proof_image_url}
    )

    # Notify citizens who reported this issue
    reports = db.query(Report).filter(Report.issue_id == issue.id).all()
    for rep in reports:
        if rep.user_id:
            notification_service.notify_user(
                db=db,
                user_id=rep.user_id,
                title="Issue Resolved",
                message=f"Good news! Civic Issue {issue.issue_code} that you reported has been resolved by municipal crews.",
                related_issue_id=issue.id
            )

    db.commit()
    db.refresh(resolution)
    return resolution

@router.post("/resolution/{resolution_id}/verify", response_model=ResolutionResponse)
def verify_resolution(
    resolution_id: str,
    verify_in: ResolutionVerifyRequest,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_active_admin)
):
    """
    Quality verification check by supervising administrator before permanent sign-off.
    """
    res = db.query(ResolutionRecord).filter(ResolutionRecord.id == resolution_id).first()
    if not res:
        raise HTTPException(status_code=404, detail="Resolution record not found.")

    res.is_verified = verify_in.is_verified
    res.verified_by_user_id = current_admin.id
    res.verification_notes = verify_in.verification_notes
    res.verified_at = datetime.utcnow()

    issue = db.query(Issue).filter(Issue.id == res.issue_id).first()
    if issue:
        if verify_in.is_verified:
            issue.verified_at = datetime.utcnow()
        else:
            # Reopen issue if verification rejected
            issue.status = IssueStatus.IN_PROGRESS

    audit_service.log_action(
        db=db,
        user_id=current_admin.id,
        action="RESOLUTION_VERIFIED" if verify_in.is_verified else "RESOLUTION_REJECTED",
        entity_type="RESOLUTION",
        entity_id=res.id,
        details={"is_verified": verify_in.is_verified, "notes": verify_in.verification_notes}
    )

    db.commit()
    db.refresh(res)
    return res
