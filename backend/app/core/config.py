import os
from typing import List
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "CivicSense – AI-Powered Civic Issue Intelligence"
    API_V1_STR: str = "/api/v1"
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./civicsense.db")
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "civicsense-dev-secret-key-change-in-production-2026")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # Uploads
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", os.path.abspath("./backend/uploads"))
    MAX_UPLOAD_SIZE_MB: int = 15
    ALLOWED_IMAGE_TYPES: List[str] = ["image/jpeg", "image/png", "image/webp"]
    
    # ML & Duplicate Detection Config
    MODEL_WEIGHTS_PATH: str = os.getenv("MODEL_WEIGHTS_PATH", "./ml/weights/yolo11_civic.pt")
    DUPLICATE_AUTO_MERGE_THRESHOLD: float = 0.85
    DUPLICATE_MANUAL_REVIEW_THRESHOLD: float = 0.65
    DUPLICATE_SEARCH_RADIUS_METERS: float = 150.0
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "*"
    ]

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()

# Ensure uploads directory exists
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
