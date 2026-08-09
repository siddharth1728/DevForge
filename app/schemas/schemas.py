from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

# --- USER SCHEMAS ---
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    github_username: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    full_name: str
    github_username: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

# --- TOKEN SCHEMAS ---
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

# --- PROJECT SCHEMAS ---
class ProjectCreate(BaseModel):
    title: str
    description: Optional[str] = None
    tech_stack: str  # e.g., "Python, FastAPI, PostgreSQL"
    github_url: Optional[str] = None
    live_url: Optional[str] = None
    status: Optional[str] = "in_progress"

class ProjectUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    tech_stack: Optional[str] = None
    github_url: Optional[str] = None
    live_url: Optional[str] = None
    status: Optional[str] = None

class ProjectResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    tech_stack: str
    github_url: Optional[str] = None
    live_url: Optional[str] = None
    status: str
    created_at: datetime
    owner_id: int

    class Config:
        from_attributes = True

# --- DASHBOARD & ANALYTICS SCHEMAS ---
class DashboardStatsResponse(BaseModel):
    total_projects: int
    completed_projects: int
    in_progress_projects: int
    top_languages: List[str]
    github_username: Optional[str] = None
    github_repos: int = 0
    github_stars: int = 0

# --- AI INSIGHTS SCHEMAS ---
class AIResumeInsightsResponse(BaseModel):
    portfolio_score: int
    strengths: List[str]
    missing_skills: List[str]
    recommendations: List[str]
