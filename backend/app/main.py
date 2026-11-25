import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from backend.app.core.config import settings
from backend.app.core.database import engine, Base, SessionLocal
from backend.app.api.api_router import api_router
from backend.app.utils.seed_data import init_db_data

# Ensure tables and seed data
Base.metadata.create_all(bind=engine)
with SessionLocal() as db_session:
    try:
        init_db_data(db_session)
    except Exception as e:
        print(f"[Startup Warning] Could not seed database: {e}")

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Intelligent Civic Issue Management platform with Deep Learning Object Detection, Image Embedding Similarity, and Geospatial Intelligence.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static file serving for uploads & samples
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
samples_dir = os.path.abspath("./backend/samples")
os.makedirs(samples_dir, exist_ok=True)

app.mount("/static/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")
app.mount("/static/samples", StaticFiles(directory=samples_dir), name="samples")

# Mount API V1
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "CivicSense Core API",
        "version": "1.0.0",
        "model_loaded": True
    }

# Mount Production Frontend Dist if built
frontend_dist = os.path.abspath("./frontend/dist")
if os.path.exists(frontend_dist):
    app.mount("/assets", StaticFiles(directory=os.path.join(frontend_dist, "assets")), name="frontend-assets")
    
    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        # Don't hijack API or static routes
        if full_path.startswith("api") or full_path.startswith("static") or full_path.startswith("docs"):
            return None
        file_path = os.path.join(frontend_dist, full_path)
        if os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse(os.path.join(frontend_dist, "index.html"))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=True)
