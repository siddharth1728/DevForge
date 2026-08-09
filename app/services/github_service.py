import json
import urllib.request
from typing import Dict, Any, List
from fastapi import HTTPException, status
import datetime

from app.config.config import GITHUB_TOKEN

GITHUB_API_BASE = "https://api.github.com"

def fetch_github_user_repos(username: str) -> List[Dict[str, Any]]:
    """Fetches public repositories for a given GitHub username via GitHub REST API."""
    url = f"{GITHUB_API_BASE}/users/{username}/repos?per_page=100&sort=updated"
    
    headers = {
        "User-Agent": "DevForge-Backend-App",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    if GITHUB_TOKEN:
        headers["Authorization"] = f"Bearer {GITHUB_TOKEN}"

    req = urllib.request.Request(url, headers=headers)
    
    try:
        with urllib.request.urlopen(req) as response:
            if response.status == 200:
                data = json.loads(response.read().decode('utf-8'))
                return data
            else:
                raise HTTPException(
                    status_code=response.status,
                    detail=f"Failed to fetch GitHub repositories for user '{username}'"
                )
    except urllib.error.HTTPError as e:
        if e.code == 404:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"GitHub user '{username}' not found. Please check the spelling or connect a valid account."
            )
        elif e.code in (403, 429):
            remaining = e.headers.get("x-ratelimit-remaining")
            reset_time = e.headers.get("x-ratelimit-reset")
            
            is_rate_limit = (remaining == '0' or e.code == 429)
            
            if is_rate_limit:
                msg = "GitHub API rate limit exceeded. Please try again later."
                if reset_time:
                    try:
                        reset_dt = datetime.datetime.fromtimestamp(int(reset_time))
                        reset_str = reset_dt.strftime("%H:%M")
                        msg = f"GitHub API rate limit exceeded. Please try again after {reset_str}."
                    except Exception:
                        pass
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=msg
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="GitHub API access forbidden."
                )
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"GitHub API Error: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to connect to GitHub API: {str(e)}"
        )

def analyze_github_stats(repos: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calculates repository counts, total stars, and estimated language distribution from repo list."""
    total_stars = 0
    language_counts: Dict[str, int] = {}
    repo_list = []

    for repo in repos:
        if repo.get("fork"):
            continue  # Skip forked repositories
        
        stars = repo.get("stargazers_count", 0)
        total_stars += stars
        lang = repo.get("language")
        
        # Use repository size (in KB) to estimate language distribution
        size = repo.get("size", 1)  # default to 1 if size is 0 or missing to still count the repo
        if lang:
            language_counts[lang] = language_counts.get(lang, 0) + size
            
        repo_list.append({
            "name": repo.get("name"),
            "description": repo.get("description"),
            "stars": stars,
            "language": lang,
            "html_url": repo.get("html_url"),
            "updated_at": repo.get("updated_at")
        })

    # Sort repositories by updated_at descending before truncating
    repo_list.sort(key=lambda x: x.get("updated_at") or "", reverse=True)

    return {
        "total_repos": len(repo_list),
        "total_stars": total_stars,
        "languages": language_counts,
        "repos": repo_list[:10]  # Top 10 most recent repos
    }
