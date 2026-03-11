"""
Job recommendation router.
"""

from __future__ import annotations

from typing import Dict, Optional

from fastapi import APIRouter, Depends, Body

from services.orchestrator import Orchestrator, get_orchestrator
from schemas.api_models import JobRecommendationsQuery

router = APIRouter(prefix="/job-recommendations", tags=["recommendation"])


@router.get("")
def job_recommendations_get(
    query: JobRecommendationsQuery = Depends(JobRecommendationsQuery.as_query),
    orchestrator: Orchestrator = Depends(get_orchestrator),
):
    """
    Get job recommendations (GET method).
    Uses vector store-based matching or AI if available.
    """
    return orchestrator.get_job_recommendations(
        skills=query.skills,
        domain=query.domain,
        experience_level=query.experience_level,
        top_n=query.top_n,
        resume_data=None,  # GET requests don't have body
    )


@router.post("")
def job_recommendations_post(
    query: JobRecommendationsQuery = Depends(JobRecommendationsQuery.as_query),
    resume_data: Optional[Dict] = Body(None, description="Optional resume data for AI-powered recommendations"),
    orchestrator: Orchestrator = Depends(get_orchestrator),
):
    """
    Get job recommendations (POST method).
    
    If resume_data is provided, uses AI to generate diverse, personalized recommendations.
    Otherwise, uses vector store-based matching.
    """
    return orchestrator.get_job_recommendations(
        skills=query.skills,
        domain=query.domain,
        experience_level=query.experience_level,
        top_n=query.top_n,
        resume_data=resume_data,
    )


