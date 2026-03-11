"""
Context builder for Module 6 (AI Career Assistant).

Why this matters:
- RAG reduces hallucinations by grounding answers in retrieved context.
- Resume-aware context makes recommendations personalized and actionable.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

from models.skill_report import SkillGapReport


@dataclass
class ContextChunk:
    content: str
    source_type: str
    document_id: str
    score: float


def build_context(
    *,
    question: str,
    resume_json: Optional[Dict],
    skill_gap_report: Optional[SkillGapReport],
    job_recommendations: Optional[Dict],
    retrieved_chunks: Sequence[ContextChunk],
    max_chunks: int = 6,
) -> Tuple[str, List[str]]:
    """
    Build a consolidated context string and source list for prompt injection.
    """
    sections: List[str] = []
    sources: List[str] = []

    resume_section = _format_resume(resume_json)
    if resume_section:
        sections.append("Resume Profile:\n" + resume_section)
        sources.append("Resume Profile")

    gap_section = _format_skill_gap(skill_gap_report)
    if gap_section:
        sections.append("Skill Gap Summary:\n" + gap_section)
        sources.append("Skill Gap Analysis")

    jobs_section = _format_job_recommendations(job_recommendations)
    if jobs_section:
        sections.append("Job Recommendations:\n" + jobs_section)
        sources.append("Job Recommendations")

    # Rank retrieved context by relevance score
    ranked_chunks = sorted(retrieved_chunks, key=lambda c: c.score, reverse=True)[:max_chunks]
    if ranked_chunks:
        snippet_lines: List[str] = []
        for idx, chunk in enumerate(ranked_chunks, start=1):
            label = _format_source_label(chunk)
            snippet_lines.append(f"[{idx}] {label}\n{chunk.content.strip()}")
            sources.append(label)
        sections.append("Retrieved Knowledge Snippets:\n" + "\n\n".join(snippet_lines))

    if not sections:
        sections.append(
            "No relevant context was found. If you cannot answer reliably, respond with a brief request for more info."
        )

    context = "\n\n".join(sections)
    sources = _dedupe_sources(sources)
    return context, sources


def _format_resume(resume_json: Optional[Dict]) -> str:
    if not resume_json:
        return ""

    lines: List[str] = []
    name = resume_json.get("name")
    if name:
        lines.append(f"Name: {name}")

    skills = resume_json.get("skills") or []
    if skills:
        lines.append("Skills: " + ", ".join(skills[:20]))

    education = resume_json.get("education") or []
    if education:
        lines.append("Education: " + "; ".join(education[:5]))

    experience = resume_json.get("experience") or []
    if experience:
        lines.append("Experience: " + "; ".join(experience[:5]))

    return "\n".join(lines)


def _format_skill_gap(report: Optional[SkillGapReport]) -> str:
    if not report:
        return ""

    lines: List[str] = []
    if report.readiness_score:
        lines.append(f"Readiness score: {report.readiness_score}/100")
    if report.matched_skills:
        lines.append("Matched skills: " + ", ".join(report.matched_skills[:10]))
    if report.partial_skills:
        lines.append("Partial skills: " + ", ".join(report.partial_skills[:10]))
    if report.missing_skills:
        lines.append("Missing skills: " + ", ".join(report.missing_skills[:10]))
    if report.summary:
        lines.append("Summary: " + report.summary)
    return "\n".join(lines)


def _format_job_recommendations(job_recommendations: Optional[Dict]) -> str:
    if not job_recommendations:
        return ""

    jobs = job_recommendations.get("recommended_jobs") or []
    if not jobs:
        return ""

    lines: List[str] = []
    for job in jobs[:5]:
        title = job.get("job_title") or "Job Role"
        score = job.get("match_score")
        matched = job.get("matched_skills") or []
        missing = job.get("missing_skills") or []
        line = f"- {title} (match {score}%)"
        if matched:
            line += f" | matched: {', '.join(matched[:5])}"
        if missing:
            line += f" | missing: {', '.join(missing[:5])}"
        lines.append(line)
    return "\n".join(lines)


def _format_source_label(chunk: ContextChunk) -> str:
    source_map = {
        "job": "Job Description",
        "skills": "Skill Reference",
        "learning": "Learning Resource",
        "resume": "Resume Context",
    }
    base = source_map.get(chunk.source_type, chunk.source_type.title())
    doc = chunk.document_id or "Unknown"
    return f"{base}: {doc}"


def _dedupe_sources(sources: Iterable[str]) -> List[str]:
    seen = set()
    deduped: List[str] = []
    for item in sources:
        if item in seen:
            continue
        seen.add(item)
        deduped.append(item)
    return deduped
