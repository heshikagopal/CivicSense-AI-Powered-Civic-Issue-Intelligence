from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.models.user import User
from backend.app.models.issue import Issue
from backend.app.models.report import Report
from backend.app.models.duplicate import DuplicateMatch, DuplicateReviewStatus
from backend.app.schemas.duplicate import DuplicateCandidate, DuplicateCheckRequest, DuplicateReviewRequest
from backend.app.api.deps import get_current_active_officer
from backend.app.services.duplicate_service import duplicate_service
from backend.app.services.audit_service import audit_service

router = APIRouter(tags=["Duplicate Analysis"])

@router.post("/duplicates/check", response_model=List[DuplicateCandidate])
def check_duplicates(
    req: DuplicateCheckRequest,
    db: Session = Depends(get_db)
):
    """
    Evaluates geospatial and visual similarity against active complaints.
    Returns ranked duplicate candidates with recommended action.
    """
    candidates = duplicate_service.evaluate_duplicate_candidates(
        db=db,
        latitude=req.latitude,
        longitude=req.longitude,
        category_code=req.category_code
    )
    return candidates

@router.post("/duplicates/{match_id}/review")
def review_duplicate_match(
    match_id: str,
    review_in: DuplicateReviewRequest,
    db: Session = Depends(get_db),
    current_officer: User = Depends(get_current_active_officer)
):
    """
    Administrative review of duplicate candidate match.
    Allows confirmed linking or rejection with audit record.
    """
    match = db.query(DuplicateMatch).filter(DuplicateMatch.id == match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Duplicate match record not found.")

    if review_in.decision == "CONFIRM_DUPLICATE":
        match.review_status = DuplicateReviewStatus.CONFIRMED
        # Link report to candidate issue
        report = db.query(Report).filter(Report.id == match.report_id).first()
        if report and report.issue_id != match.candidate_issue_id:
            old_issue_id = report.issue_id
            report.issue_id = match.candidate_issue_id
            # Increase report count on target issue
            target_issue = db.query(Issue).filter(Issue.id == match.candidate_issue_id).first()
            if target_issue:
                target_issue.report_count += 1
    else:
        match.review_status = DuplicateReviewStatus.REJECTED

    match.reviewed_by_id = current_officer.id
    match.review_notes = review_in.review_notes

    audit_service.log_action(
        db=db,
        user_id=current_officer.id,
        action=f"DUPLICATE_{review_in.decision}",
        entity_type="DUPLICATE_MATCH",
        entity_id=match.id,
        details={"decision": review_in.decision, "notes": review_in.review_notes}
    )

    db.commit()
    return {"message": f"Duplicate review submitted: {review_in.decision}", "status": match.review_status}
