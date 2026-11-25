from datetime import datetime
from typing import Dict, Any, Optional
from backend.app.models.issue import PriorityBand

class PriorityService:
    """
    Explainable rule-based scoring engine for administrative civic triage.
    Weights:
      - Category Base Risk: 25%
      - Visible Damage Extent: 20%
      - Location Context: 20%
      - Supporting Reports: 20%
      - Evidence Quality: 10%
    Age/SLA bonus is separately tracked and bounded.
    """
    WEIGHTS = {
        "base_risk": 0.25,
        "damage_extent": 0.20,
        "location_context": 0.20,
        "supporting_reports": 0.20,
        "evidence_quality": 0.10
    }

    def compute_priority(
        self,
        base_risk_score: float,
        detection_bboxes: list = None,
        ward_density_level: str = "MEDIUM",
        report_count: int = 1,
        image_metadata: Optional[dict] = None,
        created_at: Optional[datetime] = None
    ) -> Dict[str, Any]:
        # 1. Base Risk (0 - 100)
        base_risk = max(0.0, min(100.0, float(base_risk_score)))

        # 2. Visible Damage Extent (0 - 100)
        # Derived from bounding box size coverage and quantity
        damage_extent = 40.0
        if detection_bboxes:
            total_box_area = 0.0
            for box in detection_bboxes:
                # box is [x1, y1, x2, y2]
                w = abs(box[2] - box[0])
                h = abs(box[3] - box[1])
                total_box_area += (w * h)
            # Scale box area to 0-100 score
            damage_extent = min(100.0, round(30.0 + (total_box_area * 180.0) + (len(detection_bboxes) * 10.0), 1))

        # 3. Location Context (0 - 100)
        # Higher density wards and transit routes receive higher urgency
        density_weights = {
            "CRITICAL": 95.0,
            "HIGH": 80.0,
            "MEDIUM": 55.0,
            "LOW": 30.0
        }
        location_context = density_weights.get(ward_density_level.upper(), 50.0)

        # 4. Supporting Reports (0 - 100)
        # 1 report = 25, 2 reports = 50, 3 reports = 75, 4+ reports = 100
        supporting_reports = min(100.0, round(report_count * 25.0, 1))

        # 5. Evidence Quality (0 - 100)
        evidence_quality = 75.0
        if image_metadata:
            # High resolution and valid dimensions boost evidence confidence
            w = image_metadata.get("width", 0)
            h = image_metadata.get("height", 0)
            if w >= 1280 and h >= 720:
                evidence_quality = 95.0
            elif w >= 640 and h >= 480:
                evidence_quality = 85.0
            else:
                evidence_quality = 60.0

        # Weighted calculation
        c_base = base_risk * self.WEIGHTS["base_risk"]
        c_damage = damage_extent * self.WEIGHTS["damage_extent"]
        c_loc = location_context * self.WEIGHTS["location_context"]
        c_reports = supporting_reports * self.WEIGHTS["supporting_reports"]
        c_evidence = evidence_quality * self.WEIGHTS["evidence_quality"]

        raw_score = c_base + c_damage + c_loc + c_reports + c_evidence

        # Optional SLA / Age bonus (up to 10 points for older unresolved issues)
        sla_bonus = 0.0
        if created_at:
            hours_open = (datetime.utcnow() - created_at).total_seconds() / 3600.0
            if hours_open > 72:
                sla_bonus = min(10.0, round((hours_open - 72) * 0.1, 1))

        total_score = min(100.0, round(raw_score + (sla_bonus * 0.5), 1))

        # Priority Bands
        if total_score >= 80.0:
            band = PriorityBand.CRITICAL
        elif total_score >= 60.0:
            band = PriorityBand.HIGH
        elif total_score >= 35.0:
            band = PriorityBand.MEDIUM
        else:
            band = PriorityBand.LOW

        factors_breakdown = {
            "base_risk": {
                "score": base_risk,
                "weight_percent": 25.0,
                "weighted_contribution": round(c_base, 2),
                "description": "Inherent civic hazard rating based on failure type."
            },
            "damage_extent": {
                "score": damage_extent,
                "weight_percent": 20.0,
                "weighted_contribution": round(c_damage, 2),
                "description": "Visual surface disruption scale estimated from AI detection."
            },
            "location_context": {
                "score": location_context,
                "weight_percent": 20.0,
                "weighted_contribution": round(c_loc, 2),
                "description": "Pedestrian and vehicular exposure level in this municipal ward."
            },
            "supporting_reports": {
                "score": supporting_reports,
                "weight_percent": 20.0,
                "weighted_contribution": round(c_reports, 2),
                "description": "Citizen confirmation volume and corroborating submissions."
            },
            "evidence_quality": {
                "score": evidence_quality,
                "weight_percent": 10.0,
                "weighted_contribution": round(c_evidence, 2),
                "description": "Clarity, resolution, and verification readiness of submitted media."
            }
        }

        return {
            "overall_score": total_score,
            "priority_band": band,
            "sla_bonus": sla_bonus,
            "factors": factors_breakdown
        }

priority_service = PriorityService()
