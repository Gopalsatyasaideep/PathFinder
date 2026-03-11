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

import logging
import os
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

print("✅ [1/5] Core imports done...")

# Initialize FastAPI app
app = FastAPI(
    title="PathFinder AI - Enhanced",
    description="AI-Powered Resume Analyzer with NVIDIA API Integration",
    version="2.0.0"
)

# Basic request logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("pathfinder")

# Initialize FastAPI app FIRST - NO router imports yet
app = FastAPI(
    title="PathFinder AI - Enhanced",
    description="AI-Powered Resume Analyzer with NVIDIA API Integration",
    version="2.0.0"
)

print("✅ FastAPI app initialized")

# Configure CORS using environment variable
origins = os.getenv("ALLOWED_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # specify the frontend host(s) in ALLOWED_ORIGINS
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

print("✅ CORS configured")

# Register error handlers FIRST
from utils.error_handler import register_error_handlers
register_error_handlers(app)

print("✅ Error handlers registered")

@app.get("/")
async def root():
    """
    Root endpoint with API information.
    """
    return {
        "service": "PathFinder AI - Enhanced",
        "version": "2.0.0",
        "status": "online"
    }

@app.get("/health")
async def health_check():
    """
    Health check - minimal version for startup diagnostics.
    """
    return {
        "status": "healthy",
        "service": "PathFinder AI - Enhanced",
        "version": "2.0.0"
    }

print("✅ Core endpoints initialized")

# NOW lazy-load routers on first use
_routers_loaded = False

def load_routers():
    """Lazy-load routers only when first request comes in"""
    global _routers_loaded
    if _routers_loaded:
        return
    
    print("⏳ Loading routers...")
    try:
        from routers import resume, chat, auth, user_history, mock_interview
        app.include_router(auth.router)
        app.include_router(resume.router)
        app.include_router(chat.router)
        app.include_router(user_history.router)
        app.include_router(mock_interview.router)
        print("✅ All routers loaded successfully")
        _routers_loaded = True
    except Exception as e:
        print(f"⚠️  WARNING: Could not load routers: {e}")
        import traceback
        traceback.print_exc()
        _routers_loaded = True  # Don't try again

@app.middleware("http")
async def load_routers_middleware(request, call_next):
    """Ensure routers are loaded on first request"""
    load_routers()
    response = await call_next(request)
    return response
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