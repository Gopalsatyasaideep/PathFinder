"""
Response builder for Module 8 (Backend API Layer).

Why this matters:
- Keeps response formatting consistent.
- Avoids duplicating formatting logic across routers.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from models.skill_report import SkillGapReport


class ResponseBuilder:
    @staticmethod
    def build_analysis_response(
        *,
        resume_summary: Dict[str, Any],
        skill_gap: SkillGapReport | Dict[str, Any],
        job_recommendations: Dict[str, Any],
        learning_path: Dict[str, Any],
    ) -> Dict[str, Any]:
        return {
            "resume_summary": resume_summary,
            "skill_gap": ResponseBuilder._skill_gap_to_dict(skill_gap),
            "job_recommendations": job_recommendations.get("recommended_jobs", []),
            "learning_path": learning_path.get("learning_path", []),
        }

    @staticmethod
    def build_job_recommendations(job_recommendations: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "recommended_jobs": job_recommendations.get("recommended_jobs", []),
        }

    @staticmethod
    def build_learning_path(learning_path: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "learning_path": learning_path.get("learning_path", []),
        }

    @staticmethod
    def _skill_gap_to_dict(skill_gap: SkillGapReport | Dict[str, Any]) -> Dict[str, Any]:
        if isinstance(skill_gap, SkillGapReport):
            return skill_gap.to_dict()
        if isinstance(skill_gap, dict):
            return skill_gap
        return {}
