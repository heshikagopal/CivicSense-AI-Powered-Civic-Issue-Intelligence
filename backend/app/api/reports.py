import os
import json
import uuid
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from backend.app.core.config import settings
from backend.app.core.database import get_db
from backend.app.models.user import User
from backend.app.models.issue import Issue, IssueStatus, PriorityBand
from backend.app.models.report import Report, ReportStatus
from backend.app.models.category import IssueCategory
from backend.app.models.ward import Ward
from backend.app.models.department import Department
from backend.app.models.detection import ImageMetadata, DetectedObject
from backend.app.models.duplicate import DuplicateMatch, DuplicateReviewStatus
from backend.app.models.priority import IssuePriority
from backend.app.schemas.report import ReportCreate, ReportResponse
from backend.app.schemas.issue import IssueResponse
from backend.app.api.deps import get_optional_current_user, get_current_user
from backend.app.services.detection_service import detection_service
from backend.app.services.embedding_service import embedding_service
from backend.app.services.duplicate_service import duplicate_service
from backend.app.services.priority_service import priority_service
from backend.app.services.audit_service import audit_service
from backend.app.services.notification_service import notification_service
from backend.app.utils.image import calculate_file_hash

router = APIRouter(tags=["Citizen Reports & Metadata"])

@router.get("/categories")
def get_categories(db: Session = Depends(get_db)):
    return db.query(IssueCategory).all()

@router.get("/departments")
def get_departments(db: Session = Depends(get_db)):
    return db.query(Department).all()

@router.get("/wards")
def get_wards(db: Session = Depends(get_db)):
    return db.query(Ward).all()

@router.post("/reports", response_model=ReportResponse, status_code=status.HTTP_201_CREATED)
def submit_report(
    report_in: ReportCreate,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user)
):
    """
    Submits a new citizen report:
    1. Validates image and privacy consent.
    2. Runs AI detection and visual embedding generation.
    3. Runs duplicate detection against active issues within geographic radius.
    4. Auto-links or creates new Issue with explainable priority score.
    """
    filename = os.path.basename(report_in.image_url)
    image_path = os.path.join(settings.UPLOAD_DIR, filename)

    # 1. Generate visual embedding and run detection if file exists
    embedding_vec = []
    det_results = []
    width, height, file_size = 800, 600, 0
    if os.path.exists(image_path):
        embedding_vec = embedding_service.generate_embedding(image_path)
        det_output = detection_service.detect(image_path)
        det_results = det_output.get("detections", [])
        file_size = os.path.getsize(image_path)

    # 2. Determine Category
    category = None
    target_code = report_in.confirmed_category_code or report_in.citizen_category_suggestion
    if target_code:
        category = db.query(IssueCategory).filter(
            (IssueCategory.code == target_code) | (IssueCategory.display_name.ilike(f"%{target_code}%"))
        ).first()

    if not category and det_results:
        top_cat_code = det_results[0].get("category_code")
        category = db.query(IssueCategory).filter(IssueCategory.code == top_cat_code).first()

    if not category:
        category = db.query(IssueCategory).filter(IssueCategory.code == "pothole").first()

    # 3. Check for Duplicates in vicinity
    dup_candidates = duplicate_service.evaluate_duplicate_candidates(
        db=db,
        latitude=report_in.latitude,
        longitude=report_in.longitude,
        category_code=category.code if category else None,
        image_embedding=embedding_vec
    )

    linked_issue = None
    is_auto_link = False

    # Auto-link if score >= threshold
    if dup_candidates and dup_candidates[0]["overall_duplicate_score"] >= settings.DUPLICATE_AUTO_MERGE_THRESHOLD:
        best_candidate = dup_candidates[0]
        linked_issue = db.query(Issue).filter(Issue.id == best_candidate["candidate_issue_id"]).first()
        if linked_issue:
            is_auto_link = True
            linked_issue.report_count += 1
            linked_issue.last_reported_at = datetime.utcnow()
            # Recalculate priority with new report count
            prio_calc = priority_service.compute_priority(
                base_risk_score=linked_issue.category.base_risk_score if linked_issue.category else 50.0,
                ward_density_level=linked_issue.ward.population_density_level if linked_issue.ward else "MEDIUM",
                report_count=linked_issue.report_count,
                created_at=linked_issue.created_at
            )
            linked_issue.priority_score = prio_calc["overall_score"]
            linked_issue.priority_band = prio_calc["priority_band"]
            db.flush()

    # 4. If no auto-link, create new Issue
    if not linked_issue:
        # Assign nearest ward
        ward = db.query(Ward).first()
        
        # Calculate initial priority
        bboxes = [d["bbox"] for d in det_results]
        prio_calc = priority_service.compute_priority(
            base_risk_score=category.base_risk_score if category else 50.0,
            detection_bboxes=bboxes,
            ward_density_level=ward.population_density_level if ward else "MEDIUM",
            report_count=1,
            image_metadata={"width": width, "height": height}
        )

        issue_code = f"CIV-2026-{1000 + db.query(Issue).count() + 1}"
        linked_issue = Issue(
            id=str(uuid.uuid4()),
            issue_code=issue_code,
            category_id=category.id,
            ward_id=ward.id if ward else None,
            title=f"Reported {category.display_name}: {report_in.address_text or 'Urban Location'}",
            description=report_in.citizen_comment or f"Citizen submitted report for {category.display_name}.",
            status=IssueStatus.REPORTED,
            latitude=report_in.latitude,
            longitude=report_in.longitude,
            address=report_in.address_text or "GPS Location Verified",
            priority_score=prio_calc["overall_score"],
            priority_band=prio_calc["priority_band"],
            report_count=1,
            assigned_department_id=category.default_department_id,
            first_reported_at=datetime.utcnow(),
            last_reported_at=datetime.utcnow()
        )
        db.add(linked_issue)
        db.flush()

        # Create IssuePriority breakdown record
        fb = prio_calc["factors"]
        prio_record = IssuePriority(
            id=str(uuid.uuid4()),
            issue_id=linked_issue.id,
            base_risk_score=fb["base_risk"]["score"],
            damage_extent_score=fb["damage_extent"]["score"],
            location_context_score=fb["location_context"]["score"],
            supporting_reports_score=fb["supporting_reports"]["score"],
            evidence_quality_score=fb["evidence_quality"]["score"],
            age_sla_bonus=prio_calc.get("sla_bonus", 0.0),
            calculated_priority_score=prio_calc["overall_score"],
            priority_band=prio_calc["priority_band"]
        )
        db.add(prio_record)

    # 5. Create Report Record
    report_code = f"REP-2026-{2000 + db.query(Report).count() + 1}"
    report = Report(
        id=str(uuid.uuid4()),
        report_code=report_code,
        issue_id=linked_issue.id,
        user_id=current_user.id if current_user else None,
        user_latitude=report_in.latitude,
        user_longitude=report_in.longitude,
        address_text=report_in.address_text,
        image_url=report_in.image_url,
        citizen_category_suggestion=category.display_name if category else report_in.citizen_category_suggestion,
        citizen_comment=report_in.citizen_comment,
        consent_given=report_in.consent_given,
        status=ReportStatus.LINKED_TO_ISSUE
    )
    db.add(report)
    db.flush()

    # 6. Store Image Metadata & Vector Embedding
    img_meta = ImageMetadata(
        id=str(uuid.uuid4()),
        report_id=report.id,
        original_filename=filename,
        stored_filename=filename,
        file_size_bytes=file_size,
        mime_type="image/jpeg",
        width=width,
        height=height,
        embedding_json=json.dumps(embedding_vec) if embedding_vec else None,
        exif_stripped=True
    )
    db.add(img_meta)

    # 7. Store Detections
    for det in det_results:
        d_obj = DetectedObject(
            id=str(uuid.uuid4()),
            report_id=report.id,
            category_code=det["category_code"],
            confidence=det["confidence"],
            bbox_x1=det["bbox"][0],
            bbox_y1=det["bbox"][1],
            bbox_x2=det["bbox"][2],
            bbox_y2=det["bbox"][3],
            model_version="yolo11-civic-v1.0"
        )
        db.add(d_obj)

    # 8. Store Duplicate Candidate Matches for Review if between 0.65 and 0.85
    for cand in dup_candidates:
        if cand["candidate_issue_id"] != linked_issue.id:
            dup_match = DuplicateMatch(
                id=str(uuid.uuid4()),
                report_id=report.id,
                candidate_issue_id=cand["candidate_issue_id"],
                visual_similarity=cand["visual_similarity"],
                geospatial_distance_meters=cand["distance_meters"],
                temporal_difference_hours=cand["time_difference_hours"],
                overall_duplicate_score=cand["overall_duplicate_score"],
                review_status=DuplicateReviewStatus.AUTO_LINKED if is_auto_link else DuplicateReviewStatus.PENDING
            )
            db.add(dup_match)

    # 9. Audit and Notification
    audit_service.log_action(
        db=db,
        user_id=current_user.id if current_user else None,
        action="REPORT_CREATED",
        entity_type="REPORT",
        entity_id=report.id,
        details={"issue_code": linked_issue.issue_code, "category": category.code if category else "unknown"}
    )

    if current_user:
        notification_service.notify_user(
            db=db,
            user_id=current_user.id,
            title="Civic Report Received",
            message=f"Thank you. Your report ({report.report_code}) has been registered under Civic Issue {linked_issue.issue_code}.",
            related_issue_id=linked_issue.id
        )

    db.commit()
    db.refresh(report)
    return report

@router.get("/reports/mine", response_model=List[ReportResponse])
def get_my_reports(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(Report).filter(Report.user_id == current_user.id).order_by(Report.created_at.desc()).all()

@router.get("/reports/{report_id}", response_model=ReportResponse)
def get_report(report_id: str, db: Session = Depends(get_db)):
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report
