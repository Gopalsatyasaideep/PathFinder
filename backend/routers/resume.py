"""
Resume Upload Router

This module defines the FastAPI endpoint for resume upload and parsing.
Handles file upload, validation, and returns parsed resume data.
"""

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status
from typing import Optional, List
from pathlib import Path

from services.orchestrator import Orchestrator, get_orchestrator
from schemas.api_models import JobRecommendationsQuery

router = APIRouter(prefix="/upload-resume", tags=["resume"])


@router.post("")
async def upload_resume(
    file: UploadFile = File(...),
    orchestrator: Orchestrator = Depends(get_orchestrator),
):
    """
    Upload and parse a resume file.

    Delegates parsing to the orchestrator so routes stay thin.
    """
    return await orchestrator.parse_resume_upload(file)


@router.post("/ats-score")
async def get_ats_score(
    file: UploadFile = File(...),
    job_description: Optional[str] = None,
    orchestrator: Orchestrator = Depends(get_orchestrator),
):
    """
    Upload resume and get ATS (Applicant Tracking System) score.
    
    Args:
        file: Resume file (PDF or DOCX)
        job_description: Optional job description to score against
        
    Returns:
        Parsed resume data with ATS score analysis
    """
    return await orchestrator.get_resume_ats_score(file, job_description)


@router.post("/analyze-with-jobs")
async def analyze_resume_with_jobs(
    file: UploadFile = File(...),
    target_role: Optional[str] = None,
    include_ats_scores: bool = True,
    orchestrator: Orchestrator = Depends(get_orchestrator),
):
    """
    Upload resume, parse it, get job recommendations, and calculate ATS scores.
    
    This is a comprehensive endpoint that:
    1. Parses the resume
    2. Generates job recommendations based on skills
    3. Calculates ATS scores for each recommended job
    
    Args:
        file: Resume file (PDF or DOCX)
        target_role: Optional target role for recommendations
        include_ats_scores: Whether to include ATS scores (default: True)
        
    Returns:
        Complete analysis with resume data, job recommendations, and ATS scores
    """
    return await orchestrator.analyze_resume_with_jobs(
        file=file,
        target_role=target_role,
        include_ats_scores=include_ats_scores
    )


@router.post("/smart-analysis")
async def smart_resume_analysis(
    file: UploadFile = File(...),
    target_role: Optional[str] = None,  # Let AI auto-detect role from resume
    num_jobs: int = 15,
    orchestrator: Orchestrator = Depends(get_orchestrator),
):
    """
    Complete AI-powered resume analysis using NVIDIA.
    
    This endpoint provides:
    - Resume parsing and extraction
    - AI-generated job recommendations from 7+ APIs (Default: 15 jobs)
    - AI auto-detects target role from resume skills (unless explicitly provided)
    - Local match scores (NO NVIDIA ATS scoring for web jobs - saves time and API costs)
    - Career insights and suggestions
    - All in one response
    
    Perfect for frontend to get everything in one call.
    Now fetches from: The Muse, RemoteOK, Arbeitnow, and more!
    
    NOTE: Web jobs are NOT sent to NVIDIA for ATS comparison to improve speed.
    Target role is auto-detected based on resume skills unless provided.
    """
    return await orchestrator.smart_resume_analysis(
        file=file,
        target_role=target_role,
        num_jobs=num_jobs
    )


@router.post("/smart-job-match")
async def smart_job_match(
    file: UploadFile = File(...),
    target_role: Optional[str] = None,
    location: str = "remote",
    max_results: int = 15,
    prioritize_india: bool = True,
):
    """
    🚀 ENHANCED: Resume-based job matching with RapidAPI JSearch.
    
    Uses your RapidAPI key to search Indeed, LinkedIn, and Glassdoor for jobs
    that match your resume skills and experience.
    
    Features:
    - Auto-detects target role from resume if not provided
    - Scores jobs based on skill match (0-100)
    - Shows matched skills and skill match percentage
    - Returns jobs sorted by relevance
    - Includes salary, company logo, qualifications, benefits
    
    Args:
        file: Resume file (PDF or DOCX)
        target_role: Desired job title (auto-detected if None)
        location: Job location or "remote"
        max_results: Number of jobs to return (default: 15)
        prioritize_india: Prioritize Indian jobs (default: True)
        
    Returns:
        {
            "resume": {...parsed resume data...},
            "jobs": [...matched jobs with scores...],
            "target_role": "Auto-detected or provided role",
            "total_jobs": 15,
            "avg_relevance_score": 75.3
        }
    """
    try:
        from services.resume_parser import ResumeParser
        from services.resume_job_matcher import get_resume_job_matcher
        
        # Parse resume
        parser = ResumeParser()
        content = await file.read()
        
        # Save temporarily
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix) as tmp:
            tmp.write(content)
            tmp_path = tmp.name
        
        try:
            resume_data = parser.parse(tmp_path)
        finally:
            # Clean up
            import os
            os.unlink(tmp_path)
        
        # Get job matcher
        matcher = get_resume_job_matcher()
        
        # Get matched jobs
        jobs = matcher.get_job_recommendations(
            resume_data=resume_data,
            target_role=target_role,
            location=location,
            max_results=max_results,
            prioritize_india=prioritize_india
        )
        
        # Calculate stats
        relevance_scores = [j.get('relevance_score', 0) for j in jobs]
        avg_score = sum(relevance_scores) / len(relevance_scores) if relevance_scores else 0
        
        # Determine final target role
        final_target_role = target_role or jobs[0].get('title', 'Software Engineer') if jobs else 'Software Engineer'
        
        return {
            "success": True,
            "resume": {
                "name": resume_data.get('name', ''),
                "email": resume_data.get('email', ''),
                "phone": resume_data.get('phone', ''),
                "skills": resume_data.get('skills', []),
                "experience": resume_data.get('experience', []),
                "education": resume_data.get('education', []),
            },
            "jobs": jobs,
            "target_role": final_target_role,
            "location": location,
            "total_jobs": len(jobs),
            "avg_relevance_score": round(avg_score, 2),
            "message": f"Found {len(jobs)} jobs matching your resume with avg relevance {avg_score:.1f}%"
        }
        
    except Exception as e:
        print(f"❌ Smart job match error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to match jobs: {str(e)}"
        )
