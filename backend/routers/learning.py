"""
Learning path router.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends

from services.orchestrator import Orchestrator, get_orchestrator
from schemas.api_models import LearningPathQuery

router = APIRouter(prefix="/learning-path", tags=["learning"])


@router.get("/detailed")
def detailed_learning_path(
    query: LearningPathQuery = Depends(LearningPathQuery.as_query),
    experience_level: str = "Mid-level",
    orchestrator: Orchestrator = Depends(get_orchestrator),
):
    """
    Get detailed learning path with NVIDIA enhancement, animations, and comprehensive information.
    
    This endpoint provides:
    - Detailed learning phases with timelines
    - Interactive skill tree and progress tracking
    - Comprehensive resources and milestones
    - Full-screen animation support
    - Career impact analysis
    
    Perfect for showing detailed learning journey with animations.
    """
    return orchestrator.get_detailed_learning_path(
        missing_skills=query.missing_skills,
        target_role=query.target_role,
        experience_level=experience_level,
        top_n=query.top_n,
    )


@router.get("")
def learning_path(
    query: LearningPathQuery = Depends(LearningPathQuery.as_query),
    orchestrator: Orchestrator = Depends(get_orchestrator),
):
    return orchestrator.get_learning_path(
        missing_skills=query.missing_skills,
        target_role=query.target_role,
        top_n=query.top_n,
    )
