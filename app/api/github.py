from fastapi import APIRouter, Depends, HTTPException, status
from typing import Optional

from app.models.models import User
from app.core.security import get_current_user
from app.services.github_service import fetch_github_user_repos, analyze_github_stats

router = APIRouter(prefix="/api/github", tags=["GitHub Integration"])

@router.get("/user-stats")
def get_my_github_stats(current_user: User = Depends(get_current_user)):
    """Fetch GitHub repositories and analytics for the currently authenticated user."""
    if not current_user.github_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No GitHub username associated with this account. Please update your profile."
        )
    
    repos = fetch_github_user_repos(current_user.github_username)
    return analyze_github_stats(repos)

@router.get("/user/{username}")
def get_any_github_stats(username: str):
    """Fetch GitHub repositories and analytics for any public GitHub username."""
    repos = fetch_github_user_repos(username)
    return analyze_github_stats(repos)
