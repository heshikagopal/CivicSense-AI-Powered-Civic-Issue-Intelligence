import json
from typing import Optional, Any
from sqlalchemy.orm import Session
from backend.app.models.audit import AuditLog

class AuditService:
    @staticmethod
    def log_action(
        db: Session,
        user_id: Optional[str],
        action: str,
        entity_type: str,
        entity_id: str,
        details: Optional[Any] = None,
        ip_address: Optional[str] = None
    ) -> AuditLog:
        details_str = json.dumps(details) if details else None
        log_entry = AuditLog(
            user_id=user_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            details_json=details_str,
            ip_address=ip_address
        )
        db.add(log_entry)
        db.commit()
        return log_entry

audit_service = AuditService()
