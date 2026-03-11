"""
Lightweight Analysis Router

Enhanced profile analysis using NVIDIA API integration
without heavy ML dependencies for better performance.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
from typing import Dict, Any

from services.lightweight_orchestrator import AnalyzeProfileOptions, LightweightOrchestrator, get_lightweight_orchestrator
from schemas.api_models import AnalyzeProfileParams

router = APIRouter(prefix="/analyze-profile", tags=["analysis"])


@router.post("")
async def analyze_profile(
    file: UploadFile = File(...),
    params: AnalyzeProfileParams = Depends(AnalyzeProfileParams.as_form),
    orchestrator: LightweightOrchestrator = Depends(get_lightweight_orchestrator),
):
    """
    Enhanced profile analysis using AI-powered insights.
    
    This endpoint:
    1. Parses the uploaded resume
    2. Generates AI-powered resume analysis (NVIDIA/OpenRouter)
    3. Provides personalized job recommendations
    4. Creates custom learning paths
    5. Falls back gracefully if AI services are unavailable
    """
    try:
        # Parse resume
        resume_summary = await orchestrator.parse_resume_upload(file)
        
        # Enhanced AI-powered analysis
        options = AnalyzeProfileOptions(
            target_role=params.target_role,
            job_domain=params.job_domain,
            experience_level=params.experience_level,
            top_k_jobs=params.top_k_jobs,
            top_n_jobs=params.top_n_jobs,
            top_n_learning=params.top_n_learning,
            include_learning_path=params.include_learning_path,
        )
        
        enhanced_analysis = orchestrator.enhanced_analyze_profile(
            resume_summary=resume_summary,
            options=options
        )
        
        return enhanced_analysis
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Profile analysis failed: {str(e)}"
        )


@router.post("/quick-analysis")
async def quick_ai_analysis(
    file: UploadFile = File(...),
    orchestrator: LightweightOrchestrator = Depends(get_lightweight_orchestrator),
):
    """
    Quick AI-powered resume analysis without full pipeline.
    Returns just the AI insights for faster processing.
    """
    try:
        # Parse resume
        resume_summary = await orchestrator.parse_resume_upload(file)
        
        # Get AI insights only
        ai_service = orchestrator.ai_service_manager
        ai_analysis = ai_service.generate_resume_analysis(resume_summary)
        
        # Get quick job recommendations
        job_recommendations = ai_service.generate_job_recommendations(
            resume_summary, 
            num_recommendations=3
        )
        
        return {
            "resume_summary": resume_summary,
            "ai_analysis": ai_analysis,
            "quick_job_recommendations": job_recommendations,
            "analysis_type": "quick_ai",
            "provider": "NVIDIA API" if hasattr(ai_service.get_primary_client(), 'model') else "OpenRouter"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Quick analysis failed: {str(e)}"
        )


@router.post("/resume-insights")
async def get_resume_insights(resume_data: dict):
    """
    Get AI insights for already parsed resume data.
    Useful when resume is already uploaded and stored.
    """
    try:
        from services.minimal_ai_service_manager import get_minimal_ai_service_manager
        
        ai_service = get_minimal_ai_service_manager()
        
        # Generate comprehensive insights
        analysis = ai_service.generate_resume_analysis(resume_data)
        job_recs = ai_service.generate_job_recommendations(resume_data, num_recommendations=5)
        
        skills = resume_data.get('skills', [])
        target_role = resume_data.get('target_role', 'Software Developer')
        learning_path = ai_service.generate_learning_path(skills, target_role)
        
        return {
            "ai_analysis": analysis,
            "job_recommendations": job_recs,
            "learning_path": learning_path,
            "insights_type": "comprehensive",
            "based_on": "existing_resume_data"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Resume insights generation failed: {str(e)}"
        )