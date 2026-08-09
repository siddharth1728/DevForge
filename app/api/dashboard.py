from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Dict, List

from app.database.database import get_db
from app.models.models import Project, User
from app.schemas.schemas import DashboardStatsResponse
from app.core.security import get_current_user
from app.services.github_service import fetch_github_user_repos, analyze_github_stats
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard & Analytics"])

@router.get("/stats", response_model=DashboardStatsResponse)
def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieve portfolio metrics and project summary statistics for the dashboard."""
    user_projects = db.query(Project).filter(Project.owner_id == current_user.id).all()
    
    total_projects = len(user_projects)
    completed_projects = sum(1 for p in user_projects if p.status == "completed")
    in_progress_projects = sum(1 for p in user_projects if p.status == "in_progress")
    
    # Aggregate languages across all tech stacks
    language_counts: Dict[str, int] = {}
    for p in user_projects:
        if p.tech_stack:
            # Tech stack can be comma-separated strings e.g., "Python, FastAPI, Postgres"
            techs = [t.strip() for t in p.tech_stack.split(",")]
            for tech in techs:
                language_counts[tech] = language_counts.get(tech, 0) + 1
                
    sorted_techs = sorted(language_counts.items(), key=lambda x: x[1], reverse=True)
    top_languages = [t[0] for t in sorted_techs[:5]]
    
    github_repos = 0
    github_stars = 0
    if current_user.github_username:
        try:
            repos = fetch_github_user_repos(current_user.github_username)
            stats = analyze_github_stats(repos)
            github_repos = stats.get("total_repos", 0)
            github_stars = stats.get("total_stars", 0)
        except Exception as e:
            logger.warning(f"Failed to fetch GitHub stats for {current_user.github_username}: {e}")
            # Do not crash the dashboard; fall back to 0

    return {
        "total_projects": total_projects,
        "completed_projects": completed_projects,
        "in_progress_projects": in_progress_projects,
        "top_languages": top_languages,
        "github_username": current_user.github_username,
        "github_repos": github_repos,
        "github_stars": github_stars
    }
