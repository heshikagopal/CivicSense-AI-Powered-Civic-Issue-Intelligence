from typing import Optional
from sqlalchemy.orm import Session
from backend.app.models.audit import Notification

class NotificationService:
    @staticmethod
    def notify_user(
        db: Session,
        user_id: str,
        title: str,
        message: str,
        notification_type: str = "INFO",
        related_issue_id: Optional[str] = None
    ) -> Notification:
        notif = Notification(
            user_id=user_id,
            title=title,
            message=message,
            notification_type=notification_type,
            related_issue_id=related_issue_id
        )
        db.add(notif)
        db.commit()
        return notif

notification_service = NotificationService()
