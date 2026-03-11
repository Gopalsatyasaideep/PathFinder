"""
PathFinder AI - Lightweight Main Application

FastAPI application optimized for NVIDIA API integration without heavy ML dependencies.
This version focuses on API-based AI services for better performance and reliability.
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

# Import only the core routers we need for lightweight operation
from routers import resume
from routers import lightweight_analysis as analysis
from routers import chat
from routers import auth
from routers import user_history
from routers import mock_interview

from schemas.api_models import JobRecommendationsQuery

# Initialize FastAPI app
app = FastAPI(
    title="PathFinder AI - Enhanced",
    description="AI-Powered Resume Analyzer with NVIDIA API Integration",
    version="2.0.0"
)

# Basic request logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("pathfinder")

@app.middleware("http")
async def log_requests(request, call_next):
    start = time.time()
    response = await call_next(request)
    duration_ms = int((time.time() - start) * 1000)
    logger.info("%s %s -> %s (%sms)", request.method, request.url.path, response.status_code, duration_ms)
    return response

# Configure CORS using environment variable
origins = os.getenv("ALLOWED_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # specify the frontend host(s) in ALLOWED_ORIGINS
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register error handlers
from utils.error_handler import register_error_handlers
register_error_handlers(app)

# Include core routers
app.include_router(auth.router)
app.include_router(resume.router)
app.include_router(analysis.router)
app.include_router(chat.router)
app.include_router(user_history.router)
app.include_router(mock_interview.router)

@app.get("/")
async def root():
    """
    Root endpoint with API information.
    """
    return {
        "service": "PathFinder AI - Enhanced",
        "version": "2.0.0",
        "description": "AI-Powered Resume Analysis with NVIDIA Integration",
        "features": [
            "Resume parsing (PDF/DOCX)",
            "AI-powered analysis (NVIDIA API)",
            "Job recommendations",
            "Learning path generation",
            "Fallback to OpenRouter API"
        ],
        "endpoints": {
            "upload_resume": "POST /upload-resume",
            "analyze_profile": "POST /analyze-profile", 
            "quick_analysis": "POST /analyze-profile/quick-analysis",
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
        "service": "PathFinder AI - Enhanced",
        "version": "2.0.0",
        "ai_services": {
            "nvidia_api": "available" if nvidia_available else "not_configured",
            "openrouter_api": "available" if openrouter_available else "not_configured",
            "primary_service": "nvidia" if nvidia_available else "openrouter" if openrouter_available else "basic_fallback"
        },
        "features": {
            "resume_parsing": "enabled",
            "ai_analysis": "enabled" if (nvidia_available or openrouter_available) else "basic_mode",
            "job_recommendations": "enabled" if (nvidia_available or openrouter_available) else "basic_mode",
            "learning_paths": "enabled" if (nvidia_available or openrouter_available) else "basic_mode"
        }
    }

# Basic job recommendations endpoint (minimal version)
@app.post("/job-recommendations")
async def get_job_recommendations(
    resume_data: dict,
):
    """
    Get job recommendations using AI services.
    """
    try:
        from services.minimal_ai_service_manager import get_minimal_ai_service_manager
        
        ai_manager = get_minimal_ai_service_manager()
        recommendations = ai_manager.generate_job_recommendations(
            resume_data, 
            num_recommendations=5
        )
        
        return {
            "recommended_jobs": recommendations,
            "message": "Job recommendations generated successfully"
        }
    except Exception as e:
        logger.error(f"Job recommendations failed: {e}")
        return {
            "recommended_jobs": [],
            "error": "Job recommendations temporarily unavailable"
        }

@app.get("/dashboard-data")
async def dashboard_data():
    """
    Dashboard data endpoint - returns empty structure.
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
    port = int(os.environ.get("PORT", 8000))
    print("PORT env:", port)
    uvicorn.run(app, host="0.0.0.0", port=port)