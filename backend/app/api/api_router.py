from fastapi import APIRouter

from backend.app.api.auth import router as auth_router
from backend.app.api.detection import router as detection_router
from backend.app.api.reports import router as reports_router
from backend.app.api.duplicates import router as duplicates_router
from backend.app.api.priorities import router as priorities_router
from backend.app.api.map import router as map_router
from backend.app.api.analytics import router as analytics_router
from backend.app.api.assignments import router as assignments_router
from backend.app.api.resolutions import router as resolutions_router
from backend.app.api.issues import router as issues_router

api_router = APIRouter()

api_router.include_router(auth_router)
api_router.include_router(detection_router)
api_router.include_router(reports_router)
api_router.include_router(duplicates_router)
api_router.include_router(priorities_router)
api_router.include_router(map_router)
api_router.include_router(analytics_router)
api_router.include_router(assignments_router)
api_router.include_router(resolutions_router)
api_router.include_router(issues_router)
