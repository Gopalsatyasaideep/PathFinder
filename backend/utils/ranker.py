"""
Ranking utilities for Module 5 (Job Recommendation Engine).

Why this exists:
- Keep retrieval logic separate from ranking/scoring.
- Make the scoring strategy swappable for future ML models.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Sequence, Tuple

import numpy as np

from embeddings.embedder import Embedder
from models.skill_report import SkillGapReport
from .similarity import max_similarities


@dataclass
class RankerConfig:
    # Similarity thresholds for skill matching (cosine similarity in [0, 1])
    match_threshold: float = 0.75
    partial_threshold: float = 0.50
    partial_weight: float = 0.50

    # Weights for overall scoring
    skill_weight: float = 0.60
    semantic_weight: float = 0.40

    # Adjust score based on the user's skill gap report
    gap_alignment_weight: float = 0.10

    # Penalize missing skills slightly beyond coverage
    missing_penalty: float = 0.15


@dataclass
class JobRankResult:
    match_score: int
    matched_skills: List[str]
    missing_skills: List[str]
    reason: str
    coverage_score: float
    semantic_score: float


class JobRanker:
    """
    Compute match quality between a resume and a job description.

    This class keeps scoring logic centralized so future ML models can
    replace the heuristic scoring without changing the retriever.
    """

    def __init__(self, embedder: Embedder, config: Optional[RankerConfig] = None):
        self.embedder = embedder
        self.config = config or RankerConfig()

    def rank_job(
        self,
        *,
        resume_skills: Sequence[str],
        job_skills: Sequence[str],
        resume_summary: str,
        job_text: str,
        skill_gap_report: Optional[SkillGapReport] = None,
    ) -> JobRankResult:
        """
        Produce a match score plus an explanation.

        Uses two signals:
        1) Skill coverage (semantic matching between skill names)
        2) Semantic similarity between resume summary and job text
        """
        matched, partial, missing, coverage = self._match_skills(
            resume_skills=resume_skills,
            job_skills=job_skills,
        )

        semantic_score = self._semantic_similarity(resume_summary, job_text)

        gap_bonus, gap_penalty = self._gap_alignment(job_skills, skill_gap_report)

        missing_ratio = len(missing) / max(1, len(job_skills))
        raw = (
            self.config.skill_weight * coverage
            + self.config.semantic_weight * semantic_score
            + self.config.gap_alignment_weight * (gap_bonus - gap_penalty)
            - self.config.missing_penalty * missing_ratio
        )
        raw = self._clamp(raw, 0.0, 1.0)
        match_score = int(round(raw * 100))

        reason = self._build_reason(
            match_score=match_score,
            matched_skills=matched,
            missing_skills=missing,
        )

        return JobRankResult(
            match_score=match_score,
            matched_skills=matched,
            missing_skills=missing,
            reason=reason,
            coverage_score=coverage,
            semantic_score=semantic_score,
        )

    def _match_skills(
        self,
        *,
        resume_skills: Sequence[str],
        job_skills: Sequence[str],
    ) -> Tuple[List[str], List[str], List[str], float]:
        if not job_skills:
            return [], [], [], 0.0

        if not resume_skills:
            return [], [], list(job_skills), 0.0

        user_vecs = self.embedder.embed_texts(list(resume_skills))
        job_vecs = self.embedder.embed_texts(list(job_skills))

        # For each job skill, find the best matching resume skill.
        scores, _ = max_similarities(job_vecs, user_vecs)

        matched: List[str] = []
        partial: List[str] = []
        missing: List[str] = []

        for skill, score_val in zip(job_skills, scores):
            if score_val >= self.config.match_threshold:
                matched.append(skill)
            elif score_val >= self.config.partial_threshold:
                partial.append(skill)
            else:
                missing.append(skill)

        total = len(job_skills)
        coverage = (len(matched) + self.config.partial_weight * len(partial)) / max(1, total)
        return matched, partial, missing, float(coverage)

    def _semantic_similarity(self, resume_summary: str, job_text: str) -> float:
        """
        Compute semantic similarity between resume summary and job text.

        RAG benefit: this captures meaning beyond keyword overlap,
        so we can match roles even if the exact wording differs.
        """
        if not resume_summary or not job_text:
            return 0.0

        vecs = self.embedder.embed_texts([resume_summary, job_text])
        # Embeddings are normalized, so dot product equals cosine similarity.
        sim = float(np.dot(vecs[0], vecs[1]))
        # Map to [0, 1] and clamp
        return self._clamp((sim + 1.0) / 2.0, 0.0, 1.0)

    def _gap_alignment(
        self,
        job_skills: Sequence[str],
        report: Optional[SkillGapReport],
    ) -> Tuple[float, float]:
        if not report or not job_skills:
            return 0.0, 0.0

        job_set = set(job_skills)
        matched_overlap = job_set.intersection(report.matched_skills)
        missing_overlap = job_set.intersection(report.missing_skills)

        total = max(1, len(job_set))
        return len(matched_overlap) / total, len(missing_overlap) / total

    @staticmethod
    def _build_reason(
        *,
        match_score: int,
        matched_skills: Sequence[str],
        missing_skills: Sequence[str],
    ) -> str:
        if match_score >= 80:
            base = "Your skills align strongly with this role."
        elif match_score >= 60:
            base = "Your skills align well with the core requirements."
        elif match_score >= 40:
            base = "You match some requirements but have notable gaps."
        else:
            base = "This role has several skill gaps for your profile."

        details: List[str] = [base]
        if matched_skills:
            details.append(
                f"Matched: {', '.join(list(matched_skills)[:5])}{'...' if len(matched_skills) > 5 else ''}."
            )
        if missing_skills:
            details.append(
                f"Missing: {', '.join(list(missing_skills)[:5])}{'...' if len(missing_skills) > 5 else ''}."
            )
        return " ".join(details)

    @staticmethod
    def _clamp(value: float, low: float, high: float) -> float:
        return max(low, min(high, value))
