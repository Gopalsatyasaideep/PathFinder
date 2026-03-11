"""
Path builder utilities for Module 7 (Personalized Learning Path Generator).

Why this matters:
- RAG keeps learning recommendations grounded in real resources.
- Phased learning (foundation → intermediate → advanced) helps users build
  skills in a structured, efficient progression.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Protocol, Sequence

from models.learning_step import LearningStep
from models.skill_report import SkillGapReport


@dataclass
class ResourceEntry:
    content: str
    source_type: str
    document_id: str
    score: float


class OutcomeGenerator(Protocol):
    def generate(
        self,
        *,
        skill: str,
        target_role: str,
        context: str,
        gap_summary: str,
    ) -> str:
        ...


PHASE_ORDER: Dict[str, int] = {
    "Foundation": 0,
    "Intermediate": 1,
    "Advanced": 2,
}


def build_learning_steps(
    *,
    missing_skills: Sequence[str],
    target_role: str,
    resource_map: Dict[str, List[ResourceEntry]],
    skill_gap_report: Optional[SkillGapReport],
    max_resources: int = 3,
    include_estimates: bool = True,
    outcome_generator: Optional[OutcomeGenerator] = None,
) -> List[LearningStep]:
    """
    Build a phased learning path from missing skills and retrieved resources.
    """
    steps: List[LearningStep] = []
    for skill in missing_skills:
        resources = resource_map.get(skill, [])
        phase, difficulty = infer_phase_and_difficulty(skill, resources)
        resources_list = format_resources(resources, max_resources=max_resources)
        outcome = build_outcome(
            skill=skill,
            target_role=target_role,
            resources=resources,
            skill_gap_report=skill_gap_report,
            generator=outcome_generator,
        )
        estimated = estimate_weeks(difficulty) if include_estimates else None

        steps.append(
            LearningStep(
                phase=phase,
                skill=skill,
                resources=resources_list,
                outcome=outcome,
                difficulty=difficulty,
                estimated_weeks=estimated,
            )
        )

    # Order by phase then by resource relevance
    steps.sort(key=lambda s: (PHASE_ORDER.get(s.phase, 99), s.skill))
    return steps


def infer_phase_and_difficulty(
    skill: str,
    resources: Sequence[ResourceEntry],
) -> tuple[str, str]:
    """
    Infer difficulty using resource content signals.
    """
    text = " ".join(
        [skill]
        + [r.document_id or "" for r in resources[:2]]
        + [r.content or "" for r in resources[:2]]
    ).lower()

    beginner_terms = ["beginner", "intro", "introduction", "basics", "fundamentals", "getting started"]
    intermediate_terms = ["intermediate", "hands-on", "practical", "project", "applied"]
    advanced_terms = ["advanced", "expert", "architecture", "optimization", "scalable", "system design"]

    if _contains_any(text, beginner_terms):
        difficulty = "Beginner"
    elif _contains_any(text, advanced_terms):
        difficulty = "Advanced"
    elif _contains_any(text, intermediate_terms):
        difficulty = "Intermediate"
    else:
        difficulty = "Intermediate"

    phase_map = {
        "Beginner": "Foundation",
        "Intermediate": "Intermediate",
        "Advanced": "Advanced",
    }
    return phase_map[difficulty], difficulty


def format_resources(resources: Sequence[ResourceEntry], *, max_resources: int) -> List[str]:
    """
    Extract links or titles from retrieved resource chunks.
    """
    if not resources:
        return []

    candidates: List[str] = []
    for entry in sorted(resources, key=lambda r: r.score, reverse=True):
        urls = _extract_urls(entry.content)
        if urls:
            candidates.extend(urls)
        else:
            label = entry.document_id or _format_source_label(entry.source_type)
            candidates.append(label)

    return _dedupe(candidates)[:max_resources]


def build_outcome(
    *,
    skill: str,
    target_role: str,
    resources: Sequence[ResourceEntry],
    skill_gap_report: Optional[SkillGapReport],
    generator: Optional[OutcomeGenerator],
) -> str:
    """
    Build an explainable learning outcome for a skill.
    """
    gap_summary = ""
    if skill_gap_report and skill_gap_report.missing_skills:
        gap_summary = ", ".join(skill_gap_report.missing_skills[:8])

    context = "\n".join([r.content.strip() for r in resources[:2] if r.content])

    if generator:
        generated = generator.generate(
            skill=skill,
            target_role=target_role,
            context=context,
            gap_summary=gap_summary,
        )
        if generated:
            return generated

    if gap_summary:
        return (
            f"Build competency in {skill} to close a skill gap for {target_role} roles. "
            f"This improves readiness for role requirements highlighted in the gap analysis."
        )

    return f"Develop proficiency in {skill} aligned with {target_role} requirements."


def estimate_weeks(difficulty: str) -> Optional[int]:
    """
    Simple time estimate per phase (optional).
    """
    estimates = {
        "Beginner": 2,
        "Intermediate": 3,
        "Advanced": 4,
    }
    return estimates.get(difficulty)


def _format_source_label(source_type: str) -> str:
    source_map = {
        "learning": "Learning Resource",
        "skills": "Skill Reference",
        "job": "Job Description",
    }
    return source_map.get(source_type, source_type.title())


def _extract_urls(text: str) -> List[str]:
    if not text:
        return []
    return re.findall(r"https?://\\S+", text)


def _contains_any(text: str, terms: Iterable[str]) -> bool:
    return any(term in text for term in terms)


def _dedupe(items: Iterable[str]) -> List[str]:
    seen = set()
    result: List[str] = []
    for item in items:
        if item in seen:
            continue
        seen.add(item)
        result.append(item)
    return result
