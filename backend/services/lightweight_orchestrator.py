"""
Lightweight Orchestrator for NVIDIA API Integration

Simplified orchestrator that focuses on resume parsing and AI API integration
without heavy ML dependencies for faster startup and better reliability.
"""

from __future__ import annotations

import os
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

from fastapi import UploadFile, status

from .resume_parser import ResumeParser
from .minimal_ai_service_manager import MinimalAIServiceManager, get_minimal_ai_service_manager
from utils.error_handler import APIError


@dataclass
class AnalyzeProfileOptions:
    target_role: str
    job_domain: Optional[str] = None
    experience_level: Optional[str] = None
    top_k_jobs: int = 10
    top_n_jobs: int = 5
    top_n_learning: int = 6
    include_learning_path: bool = True


class LightweightOrchestrator:
    """
    Lightweight orchestration layer focused on AI API integration.
    Avoids heavy ML dependencies for better performance.
    """

    def __init__(self):
        self.resume_parser = ResumeParser()
        self._ai_service_manager: Optional[MinimalAIServiceManager] = None

    @property
    def ai_service_manager(self) -> MinimalAIServiceManager:
        """Lazy initialization of AI service manager."""
        if self._ai_service_manager is None:
            self._ai_service_manager = get_minimal_ai_service_manager()
        return self._ai_service_manager

    async def parse_resume_upload(self, file: UploadFile) -> Dict[str, Any]:
        """
        Parse a resume file into structured JSON.
        """
        if not file or not file.filename:
            raise APIError("Resume file is required.", status_code=status.HTTP_400_BAD_REQUEST)

        file_extension = Path(file.filename).suffix.lower()
        if file_extension not in {".pdf", ".docx"}:
            raise APIError("Invalid file type. Allowed types: PDF, DOCX.", status_code=status.HTTP_400_BAD_REQUEST)

        file_type = "pdf" if file_extension == ".pdf" else "docx"

        contents = await file.read()
        max_size = 5 * 1024 * 1024
        if len(contents) > max_size:
            raise APIError("File size exceeds 5MB limit.", status_code=status.HTTP_400_BAD_REQUEST)

        temp_file_path = None
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
                temp_file.write(contents)
                temp_file_path = temp_file.name

            return self.resume_parser.parse_resume(temp_file_path, file_type)
        except ValueError as exc:
            raise APIError(str(exc), status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)
        except Exception as exc:
            raise APIError(f"Unexpected error during parsing: {exc}", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
        finally:
            if temp_file_path and os.path.exists(temp_file_path):
                try:
                    os.unlink(temp_file_path)
                except Exception:
                    pass

    def enhanced_analyze_profile(
        self,
        *,
        resume_summary: Dict[str, Any],
        options: AnalyzeProfileOptions,
    ) -> Dict[str, Any]:
        """
        Enhanced profile analysis using AI services.
        """
        if not options.target_role:
            raise APIError("Target role is required for analysis.", status_code=status.HTTP_400_BAD_REQUEST)

        try:
            ai_service = self.ai_service_manager
            
            # Generate AI-powered resume analysis
            ai_analysis = ai_service.generate_resume_analysis(resume_summary)
            
            # Generate AI-powered job recommendations  
            ai_job_recommendations = ai_service.generate_job_recommendations(
                resume_summary,
                num_recommendations=options.top_n_jobs
            )
            
            # Generate AI-powered learning path if requested
            ai_learning_path = None
            if options.include_learning_path:
                current_skills = resume_summary.get('skills', [])
                ai_learning_path = ai_service.generate_learning_path(
                    current_skills,
                    options.target_role,
                    timeline="3 months"
                )
            
            # Build comprehensive response
            return {
                "resume_summary": resume_summary,
                "ai_analysis": ai_analysis,
                "job_recommendations": ai_job_recommendations,
                "learning_path": ai_learning_path,
                "analysis_metadata": {
                    "target_role": options.target_role,
                    "job_domain": options.job_domain,
                    "experience_level": options.experience_level,
                    "analysis_type": "ai_enhanced",
                    "timestamp": str(Path(__file__).stat().st_mtime)
                }
            }
            
        except Exception as e:
            # Fallback to basic analysis
            print(f"AI analysis failed, using basic fallback: {e}")
            
            skills = resume_summary.get('skills', [])
            return {
                "resume_summary": resume_summary,
                "ai_analysis": {
                    "strengths": skills[:3] if skills else ["Resume processed"],
                    "improvements": ["AI analysis temporarily unavailable"],
                    "career_level": "mid",
                    "industry_fit": "technology",
                    "skill_gaps": ["AI analysis needed"]
                },
                "job_recommendations": self._basic_job_recommendations(resume_summary, options.top_n_jobs),
                "learning_path": self._basic_learning_path(resume_summary, options.target_role) if options.include_learning_path else None,
                "analysis_metadata": {
                    "target_role": options.target_role,
                    "analysis_type": "basic_fallback",
                    "error": "AI services temporarily unavailable"
                }
            }

    def get_job_recommendations(
        self,
        *,
        skills: list[str],
        domain: Optional[str],
        experience_level: Optional[str],
        top_n: int,
        resume_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Get job recommendations using AI services.
        """
        try:
            # Build resume data from available information
            resume_summary = {}
            if resume_data:
                resume_summary = resume_data.copy()
            if not resume_summary.get("skills") and skills:
                resume_summary["skills"] = skills
            
            ai_service = self.ai_service_manager
            recommendations = ai_service.generate_job_recommendations(
                resume_summary,
                num_recommendations=top_n
            )
            
            return {
                "recommended_jobs": recommendations,
                "message": "AI-generated job recommendations",
                "metadata": {
                    "domain": domain,
                    "experience_level": experience_level,
                    "total_recommendations": len(recommendations)
                }
            }
            
        except Exception as e:
            print(f"Job recommendations failed: {e}")
            return {
                "recommended_jobs": self._basic_job_recommendations({"skills": skills}, top_n),
                "message": "Basic job recommendations (AI temporarily unavailable)",
                "error": str(e)
            }

    def _basic_job_recommendations(self, resume_data: Dict, num_recommendations: int) -> list:
        """Fallback job recommendations."""
        skills = resume_data.get('skills', [])
        return [
            {
                "title": f"Software Developer {i+1}",
                "company_type": "Technology Company",
                "salary_range": "$70,000 - $90,000",
                "description": "Great opportunity matching your background",
                "required_skills": skills[:3] if skills else ["Programming"],
                "match_score": 80 - (i * 5),
                "growth_potential": "Strong potential"
            } for i in range(num_recommendations)
        ]

    def _basic_learning_path(self, resume_data: Dict, target_role: str) -> Dict:
        """Fallback learning path."""
        current_skills = resume_data.get('skills', [])
        return {
            "skill_gaps": ["AI-powered analysis needed"],
            "learning_phases": [
                {
                    "title": f"Path to {target_role}",
                    "duration": "3 months",
                    "topics": ["Skill development", "Career advancement"],
                    "resources": ["Online courses", "Professional development"]
                }
            ],
            "milestones": ["Build skills", "Gain experience", "Apply for roles"],
            "estimated_hours": 80,
            "priority_order": current_skills[:3] if current_skills else ["Core skills"]
        }


# Global instance for dependency injection
_lightweight_orchestrator = None

def get_lightweight_orchestrator() -> LightweightOrchestrator:
    """Get or create the lightweight orchestrator instance."""
    global _lightweight_orchestrator
    if _lightweight_orchestrator is None:
        _lightweight_orchestrator = LightweightOrchestrator()
    return _lightweight_orchestrator