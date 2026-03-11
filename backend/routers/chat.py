"""
Chat router for the RAG-based AI Career Assistant.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends

from services.orchestrator import Orchestrator, get_orchestrator
from schemas.api_models import ChatRequest

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("")
def chat(
    payload: ChatRequest,
    orchestrator: Orchestrator = Depends(get_orchestrator),
):
    question = payload.get_question()
    if not question:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either 'question' or 'message' field is required"
        )
    
    # Get chat history context
    history_context = payload.get_history_context()
    
    return orchestrator.chat(
        question=question,
        chat_history=history_context,
        resume_json=payload.resume_json,
        skill_gap_report=payload.skill_gap_report,
        job_recommendations=payload.job_recommendations,
    )
