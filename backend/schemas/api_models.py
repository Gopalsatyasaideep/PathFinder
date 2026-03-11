"""
Pydantic schemas for Module 8 (Backend API Layer).

These schemas validate incoming requests and keep the API robust.
"""

from __future__ import annotations

from typing import Dict, List, Optional

from fastapi import Form, Query
from pydantic import BaseModel, Field, field_validator, model_validator


class AnalyzeProfileParams(BaseModel):
    target_role: str = Field(..., min_length=2)
    job_domain: Optional[str] = None
    experience_level: Optional[str] = None
    top_k_jobs: int = Field(10, ge=1, le=50)
    top_n_jobs: int = Field(5, ge=1, le=20)
    top_n_learning: int = Field(6, ge=1, le=20)
    include_learning_path: bool = True

    @classmethod
    def as_form(
        cls,
        target_role: str = Form(...),
        job_domain: Optional[str] = Form(None),
        experience_level: Optional[str] = Form(None),
        top_k_jobs: int = Form(10),
        top_n_jobs: int = Form(5),
        top_n_learning: int = Form(6),
        include_learning_path: bool = Form(True),
    ) -> "AnalyzeProfileParams":
        return cls(
            target_role=target_role,
            job_domain=job_domain,
            experience_level=experience_level,
            top_k_jobs=top_k_jobs,
            top_n_jobs=top_n_jobs,
            top_n_learning=top_n_learning,
            include_learning_path=include_learning_path,
        )

    @field_validator("job_domain", "experience_level", mode="before")
    @classmethod
    def _empty_to_none(cls, value: Optional[str]) -> Optional[str]:
        if isinstance(value, str) and not value.strip():
            return None
        return value


class JobRecommendationsQuery(BaseModel):
    skills: List[str] = Field(default_factory=list)
    domain: Optional[str] = None
    experience_level: Optional[str] = None
    top_n: int = Field(5, ge=1, le=20)

    @classmethod
    def as_query(
        cls,
        skills: Optional[List[str]] = Query(None, description="Repeat or comma-separate skills."),
        domain: Optional[str] = Query(None),
        experience_level: Optional[str] = Query(None),
        top_n: int = Query(5, ge=1, le=20),
    ) -> "JobRecommendationsQuery":
        return cls(
            skills=skills or [],
            domain=domain,
            experience_level=experience_level,
            top_n=top_n,
        )

    @field_validator("skills", mode="before")
    @classmethod
    def _split_skills(cls, value):
        if value is None:
            return []
        if isinstance(value, str):
            return [v.strip() for v in value.split(",") if v.strip()]
        if isinstance(value, list):
            flattened: List[str] = []
            for item in value:
                if isinstance(item, str):
                    flattened.extend([v.strip() for v in item.split(",") if v.strip()])
            return flattened
        return value


class LearningPathQuery(BaseModel):
    missing_skills: List[str] = Field(default_factory=list)
    target_role: str = Field(..., min_length=2)
    top_n: int = Field(6, ge=1, le=20)

    @classmethod
    def as_query(
        cls,
        missing_skills: Optional[List[str]] = Query(None, description="Repeat or comma-separate skills."),
        target_role: str = Query(...),
        top_n: int = Query(6, ge=1, le=20),
    ) -> "LearningPathQuery":
        return cls(
            missing_skills=missing_skills or [],
            target_role=target_role,
            top_n=top_n,
        )

    @field_validator("missing_skills", mode="before")
    @classmethod
    def _split_missing(cls, value):
        if value is None:
            return []
        if isinstance(value, str):
            return [v.strip() for v in value.split(",") if v.strip()]
        if isinstance(value, list):
            flattened: List[str] = []
            for item in value:
                if isinstance(item, str):
                    flattened.extend([v.strip() for v in item.split(",") if v.strip()])
            return flattened
        return value


class ChatMessage(BaseModel):
    role: str = Field(..., pattern="^(user|assistant)$")
    content: str
    timestamp: Optional[str] = None


class ChatRequest(BaseModel):
    question: Optional[str] = None
    message: Optional[str] = None
    chat_history: Optional[List[ChatMessage]] = Field(default_factory=list)
    resume_json: Optional[Dict] = None
    skill_gap_report: Optional[Dict] = None
    job_recommendations: Optional[Dict] = None

    @model_validator(mode="after")
    def validate_question_or_message(self):
        """Ensure either question or message is provided."""
        if not self.question and not self.message:
            from pydantic import ValidationError
            raise ValueError("Either 'question' or 'message' field is required")
        return self

    def get_question(self) -> str:
        """Get question from either question or message field."""
        return self.question or self.message or ""
    
    def get_history_context(self) -> str:
        """Format chat history into context string."""
        if not self.chat_history or len(self.chat_history) == 0:
            return ""
        
        # Get last 5 messages for context (avoid token limits)
        recent_messages = self.chat_history[-5:]
        history_lines = []
        for msg in recent_messages:
            role = "User" if msg.role == "user" else "Assistant"
            history_lines.append(f"{role}: {msg.content}")
        
        return "\n".join(history_lines)
