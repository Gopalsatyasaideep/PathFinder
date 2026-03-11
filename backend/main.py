"""
PathFinder AI - Main Application

FastAPI application entry point for the resume parsing module.
This module will later be extended to include RAG pipeline integration.
"""

import logging
import sys
import time
import os
from pathlib import Path

# Add backend directory to path for imports
backend_dir = Path(__file__).parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from routers import resume, analysis, recommendation, learning, chat, auth, user_history, web_jobs, mock_interview
from services.orchestrator import Orchestrator, get_orchestrator
from schemas.api_models import JobRecommendationsQuery
from utils.error_handler import register_error_handlers

# Initialize FastAPI app
app = FastAPI(
    title="PathFinder AI",
    description="Intelligent Resume Analyzer and Career Guidance System using RAG",
    version="1.0.0"
)

# Basic request logging (optional but useful for debugging)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("pathfinder")


@app.middleware("http")
async def log_requests(request, call_next):
    start = time.time()
    response = await call_next(request)
    duration_ms = int((time.time() - start) * 1000)
    logger.info("%s %s -> %s (%sms)", request.method, request.url.path, response.status_code, duration_ms)
    return response

# Configure CORS to allow frontend connections
# Uses ALLOWED_ORIGINS environment variable (comma-separated list). Defaults to all.
origins = os.getenv("ALLOWED_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(resume.router)
app.include_router(analysis.router)
app.include_router(recommendation.router)
app.include_router(learning.router)
app.include_router(chat.router)
app.include_router(auth.router)
app.include_router(user_history.router)
app.include_router(web_jobs.router)
app.include_router(mock_interview.router)

# Register centralized error handlers
register_error_handlers(app)


@app.get("/")
async def root():
    """
    Root endpoint - health check and API information.
    """
    return {
        "message": "PathFinder AI - Career Guidance API",
        "version": "1.0.0",
        "endpoints": {
            "upload_resume": "POST /upload-resume",
            "analyze_profile": "POST /analyze-profile",
            "job_recommendations": "GET /job-recommendations",
            "learning_path": "GET /learning-path",
            "chat": "POST /chat",
            "docs": "/docs",
            "health": "/health"
        }
    }


@app.get("/health")
async def health_check():
    """
    Enhanced health check endpoint with AI services status.
    """
    from services.nvidia_client import get_nvidia_client
    from services.openrouter_client import get_openrouter_client
    
    # Check AI service availability
    nvidia_available = get_nvidia_client() is not None
    openrouter_available = get_openrouter_client() is not None
    
    return {
        "status": "healthy",
        "service": "PathFinder AI",
        "ai_services": {
            "nvidia_api": "available" if nvidia_available else "not_configured",
            "openrouter_api": "available" if openrouter_available else "not_configured",
            "primary_service": "nvidia" if nvidia_available else "openrouter" if openrouter_available else "basic_fallback"
        },
        "features": {
            "resume_parsing": "enabled",
            "ai_analysis": "enabled" if (nvidia_available or openrouter_available) else "basic_mode",
            "job_recommendations": "enabled",
            "learning_paths": "enabled",
            "chat_assistant": "enabled" if (nvidia_available or openrouter_available) else "basic_mode"
        }
    }


# Compatibility endpoints for frontend
@app.get("/jobs")
async def jobs_compat(
    query: JobRecommendationsQuery = Depends(JobRecommendationsQuery.as_query),
    orchestrator: Orchestrator = Depends(get_orchestrator),
):
    """Compatibility endpoint: /jobs -> /job-recommendations"""
    return orchestrator.get_job_recommendations(
        skills=query.skills,
        domain=query.domain,
        experience_level=query.experience_level,
        top_n=query.top_n,
    )


@app.get("/dashboard-data")
async def dashboard_data(
    orchestrator: Orchestrator = Depends(get_orchestrator),
):
    """
    Dashboard data endpoint - returns empty structure for now.
    Frontend should use localStorage data from resume upload.
    """
    return {
        "name": None,
        "extractedSkills": [],
        "education": [],
        "experience": [],
        "skillGaps": [],
        "recommendedJobs": [],
        "learningPath": []
    }


if __name__ == "__main__":
    import uvicorn
    from services.nvidia_client import get_nvidia_client
    from services.openrouter_client import get_openrouter_client
    
    print("🚀 Starting PathFinder AI Backend...")
    print("=" * 50)
    
    # Check and report AI service availability
    nvidia_client = get_nvidia_client()
    openrouter_client = get_openrouter_client()
    
    print("🤖 AI Services Status:")
    if nvidia_client:
        print("   ✅ NVIDIA API - Available (Premium features)")
        primary_service = "NVIDIA API with Qwen 3 Next 80B"
    else:
        print("   ❌ NVIDIA API - Not configured")
    
    if openrouter_client:
        print("   ✅ OpenRouter API - Available (Free tier)")
        if not nvidia_client:
            primary_service = "OpenRouter API with free models"
    else:
        print("   ❌ OpenRouter API - Not configured")
    
    if not nvidia_client and not openrouter_client:
        print("   ⚠️  No AI APIs configured - using basic fallback mode")
        primary_service = "Basic fallback (limited features)"
    
    print(f"\n🎯 Primary AI Service: {primary_service}")
    print("\n💡 To enable enhanced AI features:")
    print("   • NVIDIA API: Set NVIDIA_API_KEY environment variable")
    print("   • OpenRouter API: Set OPENROUTER_API_KEY environment variable")
    print("   • Get NVIDIA key: https://build.nvidia.com/explore/discover")
    print("   • Get OpenRouter key: https://openrouter.ai/keys")
    
    print("\n🌐 Starting server...")
    print("   • Backend: http://localhost:8000")
    print("   • API Docs: http://localhost:8000/docs")
    print("   • Health Check: http://localhost:8000/health")
    print("=" * 50)
    
if __name__ == "__main__":
    import uvicorn
    import os

    port = int(os.environ.get("PORT", 8000))

    uvicorn.run(app, host="0.0.0.0", port=port)
