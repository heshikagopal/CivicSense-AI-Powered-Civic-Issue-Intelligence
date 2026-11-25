from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.models.user import User
from backend.app.models.issue import Issue, PriorityBand
from backend.app.models.priority import IssuePriority
from backend.app.schemas.issue import PriorityBreakdown, PriorityOverrideRequest
from backend.app.api.deps import get_current_active_admin
from backend.app.services.priority_service import priority_service
from backend.app.services.audit_service import audit_service

router = APIRouter(tags=["Explainable Priority Engine"])

@router.get("/issues/{issue_id}/priority", response_model=PriorityBreakdown)
def get_issue_priority(issue_id: str, db: Session = Depends(get_db)):
    issue = db.query(Issue).filter(Issue.id == issue_id).first()
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found.")

    prio_record = db.query(IssuePriority).filter(IssuePriority.issue_id == issue_id).first()
    if not prio_record:
        # Generate default breakdown
        prio_calc = priority_service.compute_priority(
            base_risk_score=issue.category.base_risk_score if issue.category else 50.0,
            ward_density_level=issue.ward.population_density_level if issue.ward else "MEDIUM",
            report_count=issue.report_count,
            created_at=issue.created_at
        )
        return {
            "issue_id": issue.id,
            "overall_score": prio_calc["overall_score"],
            "priority_band": prio_calc["priority_band"],
            "is_overridden": False,
            "override_reason": None,
            "factors": prio_calc["factors"]
        }

    # Build response from stored priority record
    w = priority_service.WEIGHTS
    factors = {
        "base_risk": {
            "score": prio_record.base_risk_score,
            "weight_percent": 25.0,
            "weighted_contribution": round(prio_record.base_risk_score * w["base_risk"], 2),
            "description": "Inherent civic hazard rating based on failure type."
        },
        "damage_extent": {
            "score": prio_record.damage_extent_score,
            "weight_percent": 20.0,
            "weighted_contribution": round(prio_record.damage_extent_score * w["damage_extent"], 2),
            "description": "Visual surface disruption scale estimated from AI detection."
        },
        "location_context": {
            "score": prio_record.location_context_score,
            "weight_percent": 20.0,
            "weighted_contribution": round(prio_record.location_context_score * w["location_context"], 2),
            "description": "Pedestrian and vehicular exposure level in this municipal ward."
        },
        "supporting_reports": {
            "score": prio_record.supporting_reports_score,
            "weight_percent": 20.0,
            "weighted_contribution": round(prio_record.supporting_reports_score * w["supporting_reports"], 2),
            "description": "Citizen confirmation volume and corroborating submissions."
        },
        "evidence_quality": {
            "score": prio_record.evidence_quality_score,
            "weight_percent": 10.0,
            "weighted_contribution": round(prio_record.evidence_quality_score * w["evidence_quality"], 2),
            "description": "Clarity, resolution, and verification readiness of submitted media."
        }
    }

    return {
        "issue_id": issue.id,
        "overall_score": issue.priority_score,
        "priority_band": issue.priority_band,
        "is_overridden": prio_record.is_overridden,
        "override_reason": prio_record.override_reason,
        "factors": factors
    }

@router.post("/issues/{issue_id}/priority/override")
def override_issue_priority(
    issue_id: str,
    override_in: PriorityOverrideRequest,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_active_admin)
):
    """
    Mandatory administrative override with justification and audit trail.
    """
    issue = db.query(Issue).filter(Issue.id == issue_id).first()
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found.")

    if not override_in.override_reason or len(override_in.override_reason.strip()) < 5:
        raise HTTPException(status_code=400, detail="A detailed mandatory override reason is required.")

    score = max(0.0, min(100.0, override_in.new_priority_score))
    if score >= 80.0:
        band = PriorityBand.CRITICAL
    elif score >= 60.0:
        band = PriorityBand.HIGH
    elif score >= 35.0:
        band = PriorityBand.MEDIUM
    else:
        band = PriorityBand.LOW

    old_score = issue.priority_score
    issue.priority_score = score
    issue.priority_band = band

    prio_record = db.query(IssuePriority).filter(IssuePriority.issue_id == issue_id).first()
    if prio_record:
        prio_record.is_overridden = True
        prio_record.overridden_by_id = current_admin.id
        prio_record.override_reason = override_in.override_reason
        prio_record.override_timestamp = datetime.utcnow()
        prio_record.calculated_priority_score = score
        prio_record.priority_band = band

    audit_service.log_action(
        db=db,
        user_id=current_admin.id,
        action="PRIORITY_OVERRIDE",
        entity_type="ISSUE",
        entity_id=issue.id,
        details={
            "old_score": old_score,
            "new_score": score,
            "new_band": band,
            "reason": override_in.override_reason
        }
    )

    db.commit()
    return {
        "message": "Priority successfully updated with administrative audit record.",
        "priority_score": score,
        "priority_band": band
    }
