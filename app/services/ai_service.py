import os
import json
from typing import List, Dict, Any
from fastapi import HTTPException, status
from pydantic import BaseModel
from google import genai
from google.genai import types

from app.config.config import GEMINI_API_KEY
from app.schemas.schemas import AIResumeInsightsResponse

def generate_portfolio_insights(projects: List[Any], github_username: str = None, github_stats: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Analyzes student portfolio projects using Google Gemini LLM and returns actionable resume & skill insights.
    """
    if not GEMINI_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="AI Insights feature is currently unavailable. Missing API configuration."
        )

    if not projects:
        return {
            "portfolio_score": 0,
            "strengths": ["Just getting started"],
            "missing_skills": ["Project experience"],
            "recommendations": ["Add at least one project before analyzing your portfolio."]
        }

    try:
        # Construct the project portfolio context for the prompt
        project_details = []
        for p in projects:
            project_details.append({
                "title": getattr(p, "title", "Untitled"),
                "description": getattr(p, "description", ""),
                "tech_stack": getattr(p, "tech_stack", ""),
                "status": getattr(p, "status", "unknown")
            })
        
        prompt = f"""
        Act as a Senior Technical Recruiter analyzing a computer science student's developer portfolio.
        The student has linked the GitHub username: {github_username or 'Not provided'}.
        
        GitHub Evidence:
        {json.dumps(github_stats, indent=2) if github_stats else 'No GitHub evidence retrieved.'}
        
        Here are their current DevForge projects:
        {json.dumps(project_details, indent=2)}
        
        Analyze these projects and the GitHub evidence (if available) to provide constructive, realistic feedback. 
        Do NOT invent metrics, skills, or achievements that aren't supported by this data.
        
        IMPORTANT: GitHub stars, repository counts, and language usage are supporting evidence and should not be treated as definitive proof of engineering skill. 
        Only reason from the available evidence shown above.
        
        Return the insights matching the expected JSON structure.
        """

        client = genai.Client(api_key=GEMINI_API_KEY)
        response = client.models.generate_content(
            model='gemini-3.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=AIResumeInsightsResponse,
                temperature=0.3,
            ),
        )

        # Parse the JSON response
        try:
            ai_data = json.loads(response.text)
            return ai_data
        except json.JSONDecodeError:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Received invalid data format from AI service."
            )

    except Exception as e:
        # Catch network/timeout or google.genai errors
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Failed to retrieve AI insights due to an external service error."
        )
