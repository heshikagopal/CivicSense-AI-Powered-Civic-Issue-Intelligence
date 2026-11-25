import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.models.user import User, UserRole
from backend.app.models.issue import Issue, IssueStatus
from backend.app.models.department import Department
from backend.app.models.assignment import DepartmentAssignment, AssignmentStatus
from backend.app.schemas.issue import IssueAssignRequest
from backend.app.api.deps import get_current_active_officer
from backend.app.services.audit_service import audit_service
from backend.app.services.notification_service import notification_service

router = APIRouter(tags=["Department Assignment"])

@router.post("/issues/{issue_id}/assign")
def assign_issue(
    issue_id: str,
    assign_in: IssueAssignRequest,
    db: Session = Depends(get_db),
    current_officer: User = Depends(get_current_active_officer)
):
    issue = db.query(Issue).filter(Issue.id == issue_id).first()
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found.")

    dept = db.query(Department).filter(Department.id == assign_in.department_id).first()
    if not dept:
        raise HTTPException(status_code=400, detail="Invalid department ID.")

    officer = None
    if assign_in.officer_id:
        officer = db.query(User).filter(User.id == assign_in.officer_id).first()

    issue.assigned_department_id = dept.id
    if officer:
        issue.assigned_officer_id = officer.id
    if issue.status == IssueStatus.REPORTED:
        issue.status = IssueStatus.IN_PROGRESS

    assignment = DepartmentAssignment(
        id=str(uuid.uuid4()),
        issue_id=issue.id,
        department_id=dept.id,
        assigned_to_user_id=officer.id if officer else None,
        assigned_by_user_id=current_officer.id,
        status=AssignmentStatus.ASSIGNED,
        notes=assign_in.notes
    )
    db.add(assignment)

    audit_service.log_action(
        db=db,
        user_id=current_officer.id,
        action="ISSUE_ASSIGNED",
        entity_type="ISSUE",
        entity_id=issue.id,
        details={
            "department": dept.name,
            "officer": officer.full_name if officer else "Unassigned",
            "notes": assign_in.notes
        }
    )

    if officer:
        notification_service.notify_user(
            db=db,
            user_id=officer.id,
            title="New Issue Assigned",
            message=f"You have been assigned to civic issue {issue.issue_code} ({dept.name}).",
            related_issue_id=issue.id
        )

    db.commit()
    return {"message": "Issue assigned successfully.", "issue_id": issue.id, "status": issue.status}
