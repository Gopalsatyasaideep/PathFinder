"""
Web Jobs Router - Endpoints for real-time job search.
"""

from __future__ import annotations

from fastapi import APIRouter, Query
from typing import List, Optional
from services.enhanced_job_recommender import get_enhanced_job_recommender


router = APIRouter(prefix="/web-jobs", tags=["web-jobs"])


@router.get("/search")
def search_web_jobs(
    query: str = Query(..., description="Job title or keywords"),
    location: str = Query("remote", description="Location or 'remote'"),
    skills: Optional[str] = Query(None, description="Comma-separated skills"),
    experience_level: str = Query("Mid-level", description="Experience level"),
    max_results: int = Query(15, ge=1, le=100),
    prioritize_india: bool = Query(True, description="Prioritize India-based jobs"),
):
    """
    Search for real job postings from multiple sources.
    Now fetches from 12+ job APIs to get comprehensive real jobs:
    - Remotive, Jobicy, RemoteOK (Remote focus)
    - IndianAPI (India jobs)
    - DevITjobs (Tech/UK)
    - The Muse, Arbeitnow (Global)
    - Plus optional APIs with keys (Adzuna, JSearch, Reed, USAJobs)
    
    NOTE: Web jobs are NOT sent to NVIDIA API for ATS comparison.
    They are displayed directly as raw job recommendations.
    
    Example:
        GET /web-jobs/search?query=Software%20Engineer&location=India&max_results=15&prioritize_india=true
    """
    skill_list = []
    if skills:
        skill_list = [s.strip() for s in skills.split(',') if s.strip()]
    
    # Get the recommender instance
    recommender = get_enhanced_job_recommender()
    
    results = recommender.get_recommendations(
        skills=skill_list,
        target_role=query,
        location=location,
        experience_level=experience_level,
        top_n=max_results,
        include_web_jobs=True,
        prioritize_india=prioritize_india,
    )
    
    return {
        "query": query,
        "location": location,
        "web_jobs": results.get('web_jobs', []),
        "recommended_jobs": results.get('recommended_jobs', []),
        "total_results": results.get('total_jobs', 0),
        "sources": results.get('sources', []),
    }


@router.get("/recommended")
def get_enhanced_recommendations(
    target_role: str = Query(..., description="Target job role"),
    location: str = Query("remote", description="Preferred location"),
    skills: Optional[str] = Query(None, description="Comma-separated skills"),
    experience_level: str = Query("Mid-level", description="Experience level"),
    top_n: int = Query(15, ge=1, le=100),
    prioritize_india: bool = Query(True, description="Prioritize India-based jobs"),
):
    """
    Get personalized job recommendations combining AI and web search.
    Fetches from 12+ APIs to ensure comprehensive quality results.
    
    APIs include: Remotive, Jobicy, IndianAPI, RemoteOK, DevITjobs, 
    The Muse, Arbeitnow, and more.
    
    NOTE: Web jobs are NOT sent to NVIDIA API for ATS comparison.
    """
    skill_list = []
    if skills:
        skill_list = [s.strip() for s in skills.split(',') if s.strip()]
    
    # Get the recommender instance
    recommender = get_enhanced_job_recommender()
    
    results = recommender.get_recommendations(
        skills=skill_list,
        target_role=target_role,
        location=location,
        experience_level=experience_level,
        top_n=top_n,
        include_web_jobs=True,
        prioritize_india=prioritize_india,
    )
    
    return {
        "target_role": target_role,
        "recommendations": results,
    }
