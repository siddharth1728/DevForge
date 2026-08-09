from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

from app.config.config import APP_NAME, APP_VERSION
from app.database.database import engine
from app.models.models import Base

# Import all API Routers
from app.api.auth import router as auth_router
from app.api.projects import router as projects_router
from app.api.github import router as github_router
from app.api.dashboard import router as dashboard_router
from app.api.ai_insights import router as ai_router

# Initialize Database Tables
Base.metadata.create_all(bind=engine)

# Create FastAPI App Instance
app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    description="DevForge - The Operating System for Student Developers. Backend REST API built with FastAPI, PostgreSQL/SQLite, SQLAlchemy, and JWT Authentication."
)

# Register API Routers
app.include_router(auth_router)
app.include_router(projects_router)
app.include_router(github_router)
app.include_router(dashboard_router)
app.include_router(ai_router)

# Serve Static UI Dashboard
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/", tags=["Health Check & UI"])
def home():
    index_path = os.path.join(static_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {
        "project": APP_NAME,
        "version": APP_VERSION,
        "status": "online",
        "message": "DevForge Backend API is running 🚀",
        "documentation": "/docs"
    }