from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.models import Project, User
from app.schemas.schemas import AIResumeInsightsResponse
from app.core.security import get_current_user
from app.services.ai_service import generate_portfolio_insights

router = APIRouter(prefix="/api/ai", tags=["AI Portfolio Insights"])

@router.get("/resume-insights", response_model=AIResumeInsightsResponse)
def get_resume_insights(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Analyzes the authenticated student's portfolio projects and provides AI-driven feedback,
    identifying core strengths, key missing skills, and actionable recommendations.
    """
    user_projects = db.query(Project).filter(Project.owner_id == current_user.id).all()
    
    github_stats = None
    if current_user.github_username:
        try:
            from app.services.github_service import fetch_github_user_repos, analyze_github_stats
            repos = fetch_github_user_repos(current_user.github_username)
            github_stats = analyze_github_stats(repos)
        except Exception:
            pass  # Fallback to None if GitHub is unavailable
            
    insights = generate_portfolio_insights(user_projects, current_user.github_username, github_stats)
    return insights
