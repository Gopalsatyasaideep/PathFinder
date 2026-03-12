"""
PathFinder AI - Lightweight Main Application

FastAPI application optimized for NVIDIA API integration without heavy ML dependencies.
This version focuses on API-based AI services for better performance and reliability.
"""

import logging
import os
import sys
import time
from pathlib import Path

# Add backend directory to path for imports
backend_dir = Path(__file__).parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from fastapi import FastAPI, Depends, Body
from fastapi.middleware.cors import CORSMiddleware
from utils.error_handler import register_error_handlers

# Basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("pathfinder")

# Initialize FastAPI app
app = FastAPI(
    title="PathFinder AI - Enhanced",
    description="AI-Powered Resume Analyzer with NVIDIA API Integration",
    version="2.0.0"
)

# Configure CORS
origins_env = os.getenv("ALLOWED_ORIGINS", "")
if origins_env:
    origins = [o.strip() for o in origins_env.split(",") if o.strip()]
    if "https://pathfinderai-psi.vercel.app" not in origins:
        origins.append("https://pathfinderai-psi.vercel.app")
else:
    origins = [
        "http://localhost:5173",
        "http://localhost:3000",
        "https://pathfinderai-psi.vercel.app",
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register error handlers
register_error_handlers(app)

# Lazy-load routers to speed up initial startup and health checks
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
        _routers_loaded = True

@app.middleware("http")
async def ensure_routers_loaded(request, call_next):
    """Ensure routers are loaded on first request"""
    if request.url.path not in ["/", "/health", "/docs", "/openapi.json"]:
        load_routers()
    response = await call_next(request)
    return response

@app.get("/")
async def root():
    return {
        "service": "PathFinder AI - Enhanced",
        "version": "2.0.0",
        "status": "online"
    }

@app.get("/health")
async def health_check():
    from services.nvidia_client import get_nvidia_client
    from services.openrouter_client import get_openrouter_client
    
    nvidia_available = get_nvidia_client() is not None
    openrouter_available = get_openrouter_client() is not None
    
    return {
        "status": "healthy",
        "service": "PathFinder AI - Enhanced",
        "version": "2.0.0",
        "ai_services": {
            "nvidia_api": "available" if nvidia_available else "not_configured",
            "openrouter_api": "available" if openrouter_available else "not_configured"
        }
    }

# Basic job recommendations endpoint (minimal version)
@app.post("/job-recommendations")
async def get_job_recommendations(resume_data: dict = Body(...)):
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
    print(f"🚀 Starting server on 0.0.0.0:{port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
