import uuid
from datetime import datetime, timedelta
import random
from sqlalchemy.orm import Session

from backend.app.core.security import get_password_hash
from backend.app.models.user import User, UserRole
from backend.app.models.department import Department
from backend.app.models.category import IssueCategory
from backend.app.models.ward import Ward
from backend.app.models.issue import Issue, IssueStatus, PriorityBand
from backend.app.models.report import Report, ReportStatus
from backend.app.models.priority import IssuePriority
from backend.app.models.assignment import DepartmentAssignment, AssignmentStatus

def init_db_data(db: Session):
    """
    Idempotent seeding of essential departments, categories, wards,
    admin/officer/citizen accounts, and initial realistic civic issues.
    """
    # 1. Departments
    departments_data = [
        {"name": "Roads & Bridges Department", "code": "ROADS", "description": "Responsible for road maintenance, pothole repairs, and bridge structural integrity.", "email": "roads@civicsense.org"},
        {"name": "Solid Waste Management", "code": "WASTE", "description": "Responsible for municipal garbage collection, sanitation, and recycling operations.", "email": "waste@civicsense.org"},
        {"name": "Electrical & Street Lighting", "code": "ELECTRIC", "description": "Responsible for municipal streetlights, traffic signals, and electrical poles.", "email": "lighting@civicsense.org"},
        {"name": "Public Works & Infrastructure", "code": "INFRA", "description": "Responsible for sidewalks, barriers, drainage, public parks, and civic structures.", "email": "infra@civicsense.org"}
    ]
    dept_map = {}
    for d in departments_data:
        existing = db.query(Department).filter(Department.code == d["code"]).first()
        if not existing:
            dept = Department(
                id=str(uuid.uuid4()),
                name=d["name"],
                code=d["code"],
                description=d["description"],
                contact_email=d["email"]
            )
            db.add(dept)
            db.flush()
            dept_map[d["code"]] = dept
        else:
            dept_map[d["code"]] = existing

    # 2. Issue Categories
    categories_data = [
        {"code": "pothole", "display_name": "Pothole", "risk": 75.0, "dept_code": "ROADS", "desc": "Cavities or depressions in road surface posing traffic hazard."},
        {"code": "road_crack", "display_name": "Road Crack", "risk": 45.0, "dept_code": "ROADS", "desc": "Longitudinal, transverse, or alligator cracking requiring sealing."},
        {"code": "garbage_pile", "display_name": "Garbage Pile", "risk": 65.0, "dept_code": "WASTE", "desc": "Illegal dumping, overflowing dumpsters, or uncollected trash accumulating."},
        {"code": "damaged_streetlight", "display_name": "Damaged Streetlight", "risk": 70.0, "dept_code": "ELECTRIC", "desc": "Broken fixtures, exposed wiring, or non-functional lighting in dark corridors."},
        {"code": "damaged_infrastructure", "display_name": "Damaged Infrastructure", "risk": 80.0, "dept_code": "INFRA", "desc": "Damaged guardrails, broken footpaths, open manholes, or compromised retaining walls."}
    ]
    cat_map = {}
    for c in categories_data:
        existing = db.query(IssueCategory).filter(IssueCategory.code == c["code"]).first()
        if not existing:
            dept = dept_map.get(c["dept_code"])
            cat = IssueCategory(
                id=str(uuid.uuid4()),
                code=c["code"],
                display_name=c["display_name"],
                description=c["desc"],
                base_risk_score=c["risk"],
                default_department_id=dept.id if dept else None
            )
            db.add(cat)
            db.flush()
            cat_map[c["code"]] = cat
        else:
            cat_map[c["code"]] = existing

    # 3. Wards
    wards_data = [
        {"num": 1, "name": "Ward 1 - Central Civic Center", "density": "HIGH"},
        {"num": 2, "name": "Ward 2 - North Riverside", "density": "MEDIUM"},
        {"num": 3, "name": "Ward 3 - South Tech Corridor", "density": "HIGH"},
        {"num": 4, "name": "Ward 4 - East Industrial Zone", "density": "MEDIUM"},
        {"num": 5, "name": "Ward 5 - West Suburbs & Greenbelt", "density": "LOW"}
    ]
    ward_list = []
    for w in wards_data:
        existing = db.query(Ward).filter(Ward.ward_number == w["num"]).first()
        if not existing:
            ward = Ward(
                id=str(uuid.uuid4()),
                ward_number=w["num"],
                name=w["name"],
                population_density_level=w["density"]
            )
            db.add(ward)
            db.flush()
            ward_list.append(ward)
        else:
            ward_list.append(existing)

    # 4. Standard Users (Admin, Officer, Citizen)
    users_data = [
        {
            "email": "admin@civicsense.org",
            "password": "Admin123!",
            "name": "Sarah Jenkins (Chief Civic Officer)",
            "role": UserRole.ADMIN,
            "dept": None
        },
        {
            "email": "officer@civicsense.org",
            "password": "Officer123!",
            "name": "Marcus Vance (Roads Field Officer)",
            "role": UserRole.OFFICER,
            "dept": dept_map.get("ROADS")
        },
        {
            "email": "citizen@civicsense.org",
            "password": "Citizen123!",
            "name": "Alex Chen (Resident)",
            "role": UserRole.CITIZEN,
            "dept": None
        }
    ]
    user_map = {}
    for u in users_data:
        existing = db.query(User).filter(User.email == u["email"]).first()
        if not existing:
            user = User(
                id=str(uuid.uuid4()),
                email=u["email"],
                hashed_password=get_password_hash(u["password"]),
                full_name=u["name"],
                role=u["role"],
                department_id=u["dept"].id if u["dept"] else None,
                is_active=True
            )
            db.add(user)
            db.flush()
            user_map[u["role"]] = user
        else:
            user_map[u["role"]] = existing

    # 5. Seed Demonstration Issues if database is fresh
    issue_count = db.query(Issue).count()
    if issue_count == 0:
        base_lat, base_lng = 12.9716, 77.5946  # Urban reference coordinates
        sample_issues_specs = [
            ("pothole", "Deep hazardous pothole on arterial road", "ROADS", 78.5, PriorityBand.HIGH, 12.9725, 77.5955, "Opposite Metro Gate 3, MG Road", IssueStatus.IN_PROGRESS),
            ("garbage_pile", "Uncollected commercial refuse blocking pedestrian walkway", "WASTE", 62.0, PriorityBand.HIGH, 12.9740, 77.5930, "Market Square Corner, 5th Cross", IssueStatus.REPORTED),
            ("damaged_streetlight", "Flickering exposed wire streetlight fixture", "ELECTRIC", 71.0, PriorityBand.HIGH, 12.9690, 77.5960, "Crossroad 12, Indiranagar Link", IssueStatus.VERIFIED),
            ("road_crack", "Longitudinal surface crack across two lanes", "ROADS", 38.0, PriorityBand.MEDIUM, 12.9760, 77.5980, "Outer Ring Flyover Approach", IssueStatus.REPORTED),
            ("damaged_infrastructure", "Compromised pedestrian guardrail near school zone", "INFRA", 84.5, PriorityBand.CRITICAL, 12.9710, 77.5920, "St. Anthony Academy Lane", IssueStatus.IN_PROGRESS),
            ("pothole", "Cluster of small potholes in residential lane", "ROADS", 34.0, PriorityBand.LOW, 12.9680, 77.5910, "14th Main, HSR Layout", IssueStatus.RESOLVED),
            ("garbage_pile", "Overflowing green bins and plastic dispersion", "WASTE", 58.0, PriorityBand.MEDIUM, 12.9750, 77.5900, "Community Park Perimeter", IssueStatus.VERIFIED),
        ]

        admin_user = user_map.get(UserRole.ADMIN)
        officer_user = user_map.get(UserRole.OFFICER)
        citizen_user = user_map.get(UserRole.CITIZEN)

        for i, (cat_code, title, dept_code, score, band, lat, lng, addr, status) in enumerate(sample_issues_specs, 1):
            cat = cat_map.get(cat_code)
            dept = dept_map.get(dept_code)
            ward = ward_list[(i - 1) % len(ward_list)]
            
            created_time = datetime.utcnow() - timedelta(days=random.randint(1, 14), hours=random.randint(2, 10))
            issue = Issue(
                id=str(uuid.uuid4()),
                issue_code=f"CIV-2026-{1000 + i}",
                category_id=cat.id,
                ward_id=ward.id,
                title=title,
                description=f"Automated civic report for {cat.display_name.lower()} at {addr}. AI inspected and verified.",
                status=status,
                latitude=lat,
                longitude=lng,
                address=addr,
                priority_score=score,
                priority_band=band,
                report_count=random.randint(1, 3),
                assigned_department_id=dept.id if dept else None,
                assigned_officer_id=officer_user.id if status in (IssueStatus.IN_PROGRESS, IssueStatus.RESOLVED) else None,
                first_reported_at=created_time,
                last_reported_at=created_time + timedelta(hours=random.randint(1, 48)),
                resolved_at=created_time + timedelta(hours=36) if status == IssueStatus.RESOLVED else None,
                verified_at=created_time + timedelta(hours=48) if status == IssueStatus.RESOLVED else None,
                created_at=created_time
            )
            db.add(issue)
            db.flush()

            # Priority Breakdown Record
            prio = IssuePriority(
                id=str(uuid.uuid4()),
                issue_id=issue.id,
                base_risk_score=cat.base_risk_score,
                damage_extent_score=random.uniform(50.0, 85.0),
                location_context_score=75.0 if ward.population_density_level == "HIGH" else 50.0,
                supporting_reports_score=min(100.0, issue.report_count * 25.0),
                evidence_quality_score=85.0,
                age_sla_bonus=5.0,
                calculated_priority_score=score,
                priority_band=band
            )
            db.add(prio)

            # Citizen Report supporting this issue
            rep = Report(
                id=str(uuid.uuid4()),
                report_code=f"REP-2026-{2000 + i}",
                issue_id=issue.id,
                user_id=citizen_user.id if citizen_user else None,
                user_latitude=lat + random.uniform(-0.0001, 0.0001),
                user_longitude=lng + random.uniform(-0.0001, 0.0001),
                address_text=addr,
                image_url=f"/static/samples/{cat_code}_sample.jpg",
                citizen_category_suggestion=cat.display_name,
                citizen_comment=f"Please resolve this {cat.display_name.lower()} promptly. It is causing disruptions.",
                consent_given=True,
                status=ReportStatus.LINKED_TO_ISSUE,
                created_at=created_time
            )
            db.add(rep)

            if status in (IssueStatus.IN_PROGRESS, IssueStatus.RESOLVED):
                assign = DepartmentAssignment(
                    id=str(uuid.uuid4()),
                    issue_id=issue.id,
                    department_id=dept.id,
                    assigned_to_user_id=officer_user.id if officer_user else None,
                    assigned_by_user_id=admin_user.id if admin_user else None,
                    status=AssignmentStatus.COMPLETED if status == IssueStatus.RESOLVED else AssignmentStatus.IN_PROGRESS,
                    notes="Dispatched field engineering inspection unit.",
                    assigned_at=created_time + timedelta(hours=4)
                )
                db.add(assign)

    db.commit()
