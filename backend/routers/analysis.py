"""
Enhanced Profile Analysis Router

Coordinates resume parsing + AI-powered analysis + job recommendations + learning path.
Uses NVIDIA API for enhanced AI capabilities with OpenRouter fallback.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
from typing import Dict, Any

from services.orchestrator import AnalyzeProfileOptions, Orchestrator, get_orchestrator
from schemas.api_models import AnalyzeProfileParams

router = APIRouter(prefix="/analyze-profile", tags=["analysis"])


@router.post("")
async def analyze_profile(
    file: UploadFile = File(...),
    params: AnalyzeProfileParams = Depends(AnalyzeProfileParams.as_form),
    orchestrator: Orchestrator = Depends(get_orchestrator),
):
    """
    Comprehensive profile analysis using AI-powered insights.
    
    This endpoint:
    1. Parses the uploaded resume
    2. Generates AI-powered resume analysis 
    3. Provides job recommendations
    4. Creates personalized learning paths
    5. Performs skill gap analysis
    """
    # Parse resume
    resume_summary = await orchestrator.parse_resume_upload(file)
    
    # Enhanced AI-powered analysis
    try:
        ai_service = orchestrator.ai_service_manager
        
        # Generate AI-powered resume analysis
        ai_analysis = ai_service.generate_resume_analysis(resume_summary)
        
        # Generate AI-powered job recommendations
        ai_job_recommendations = ai_service.generate_job_recommendations(
            resume_summary, 
            num_recommendations=params.top_n_jobs
        )
        
        # Generate AI-powered learning path if requested
        ai_learning_path = None
        if params.include_learning_path:
            current_skills = resume_summary.get('skills', [])
            ai_learning_path = ai_service.generate_learning_path(
                current_skills, 
                params.target_role, 
                timeline="3 months"
            )
        
        # Combine with traditional analysis
        options = AnalyzeProfileOptions(
            target_role=params.target_role,
            job_domain=params.job_domain,
            experience_level=params.experience_level,
            top_k_jobs=params.top_k_jobs,
            top_n_jobs=params.top_n_jobs,
            top_n_learning=params.top_n_learning,
            include_learning_path=params.include_learning_path,
        )
        
        traditional_analysis = orchestrator.analyze_profile(
            resume_summary=resume_summary, 
            options=options
        )
        
        # Enhanced response combining AI insights with traditional analysis
        enhanced_response = {
            **traditional_analysis,
            "ai_insights": {
                "resume_analysis": ai_analysis,
                "ai_job_recommendations": ai_job_recommendations,
                "ai_learning_path": ai_learning_path,
                "provider": "NVIDIA API" if hasattr(ai_service.get_primary_client(), 'model') else "OpenRouter"
            },
            "analysis_type": "enhanced_ai_powered"
        }
        
        return enhanced_response
        
    except Exception as e:
        # Fallback to traditional analysis if AI services fail
        print(f"AI analysis failed, falling back to traditional analysis: {e}")
        
        options = AnalyzeProfileOptions(
            target_role=params.target_role,
            job_domain=params.job_domain,
            experience_level=params.experience_level,
            top_k_jobs=params.top_k_jobs,
            top_n_jobs=params.top_n_jobs,
            top_n_learning=params.top_n_learning,
            include_learning_path=params.include_learning_path,
        )
        
        traditional_response = orchestrator.analyze_profile(
            resume_summary=resume_summary, 
            options=options
        )
        
        # Add fallback indicator
        traditional_response["analysis_type"] = "traditional_fallback"
        traditional_response["ai_insights"] = {
            "error": "AI analysis temporarily unavailable",
            "provider": "fallback"
        }
        
        return traditional_response


@router.post("/quick-analysis")
async def quick_ai_analysis(
    file: UploadFile = File(...),
    orchestrator: Orchestrator = Depends(get_orchestrator),
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
        
        return {
            "resume_summary": resume_summary,
            "ai_analysis": ai_analysis,
            "analysis_type": "quick_ai",
            "provider": "NVIDIA API" if hasattr(ai_service.get_primary_client(), 'model') else "OpenRouter"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Quick analysis failed: {str(e)}"
        )
