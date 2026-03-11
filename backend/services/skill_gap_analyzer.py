"""
Skill Gap Analysis Engine (Module 4)

High-level flow:
1. Take parsed resume JSON (from Module 2) + target job role string.
2. Use the vector store (Module 3) to retrieve job description chunks
   that are semantically close to the target role.
3. From those chunks, extract required skills using the same skill
   database used for resume parsing (so both sides speak the same
   "skill language").
4. Compare user skills vs required skills using semantic similarity
   (sentence-transformers embeddings), not just exact string match.
5. Produce a structured SkillGapReport with:
   - matched_skills
   - partial_skills
   - missing_skills
   - readiness_score (0–100)
   - human-readable summary
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Sequence, Set, Tuple

import numpy as np

from .skill_database import (
    SKILL_DATABASE,
    get_canonical_skill_name,
    normalize_skill,
)
from .vector_store import FaissVectorStore, build_default_kb
from embeddings.embedder import Embedder
from models.skill_report import SkillGapReport
from utils.similarity import max_similarities


@dataclass
class SkillGapConfig:
    # Similarity thresholds (cosine similarity in [0, 1])
    match_threshold: float = 0.75       # definitely have this skill
    partial_threshold: float = 0.50     # somewhat related / partial match

    # How much weight partial skills contribute to readiness
    partial_weight: float = 0.5

    # Minimum number of required skills to consider a role
    min_required_skills: int = 3


class SkillGapAnalyzer:
    """
    Skill gap analysis on top of:
    - Parsed resume JSON
    - FAISS vector store knowledge base
    - sentence-transformers embeddings

    Responsibilities are split into:
    - Retrieval (get relevant job chunks for a role)
    - Skill extraction (from job chunks)
    - Matching & scoring (resume skills vs job skills)
    """

    def __init__(
        self,
        store: FaissVectorStore,
        embedder: Optional[Embedder] = None,
        config: Optional[SkillGapConfig] = None,
    ):
        self.store = store
        # Reuse the store's embedder by default to save memory and keep dimensions aligned.
        self.embedder = embedder or store.embedder
        self.config = config or SkillGapConfig()

    # ---------- Public API ----------

    def analyze(
        self,
        resume_json: Dict,
        target_role: str,
        top_k_jobs: int = 10,
    ) -> SkillGapReport:
        """
        Main entry point.

        Args:
            resume_json: Parsed resume from Module 2 (expects "skills" list).
            target_role: Human-readable role name, e.g. "Machine Learning Engineer".
            top_k_jobs: How many job chunks to retrieve from the KB.
        """
        user_skills = self._normalize_skill_list(resume_json.get("skills") or [])

        # If resume has no skills, we can still build a "fully missing" report.
        if not user_skills:
            required = self._infer_required_skills(target_role, top_k_jobs=top_k_jobs)
            return self._score([], required)

        required_skills = self._infer_required_skills(target_role, top_k_jobs=top_k_jobs)
        return self._score(user_skills, required_skills)

    # ---------- Retrieval logic ----------

    def _infer_required_skills(
        self,
        target_role: str,
        top_k_jobs: int,
    ) -> List[str]:
        """
        Use FAISS to retrieve job description chunks relevant to the target role,
        then extract skills mentioned in those chunks.

        We purposely rely on the same SKILL_DATABASE as the resume parser to keep
        skill names consistent across modules.
        """
        # Query phrasing encourages job-related results, but FAISS ultimately
        # decides based on semantic similarity.
        query = f"key skills and technologies required for {target_role}"

        search_result = self.store.search(query, top_k=top_k_jobs)
        chunks = [
            r["content"]
            for r in search_result.get("results", [])
            if r.get("source") == "job"
        ]

        # Fallback: if KB has no labelled job chunks, just use all results.
        if not chunks:
            chunks = [r["content"] for r in search_result.get("results", [])]

        required: Set[str] = set()
        for text in chunks:
            required.update(self._extract_skills_from_text(text))

        # As a final fallback, if nothing was extracted, return an empty list.
        return sorted(required)

    def _extract_skills_from_text(self, text: str) -> Set[str]:
        """
        Extract skills from free-form text using SKILL_DATABASE.

        This mirrors the logic used in resume parsing:
        - For each known skill in the database, check if it appears in the text
          (case-insensitive, with word boundaries).
        - Map to canonical display names.
        """
        if not text:
            return set()

        text_lower = text.lower()
        found: Set[str] = set()

        for raw_skill in SKILL_DATABASE:
            # Simple word-boundary regex to avoid partial word matches.
            pattern = r"\b" + raw_skill.replace("+", r"\+") + r"\b"

            if __import__("re").search(pattern, text_lower):
                canonical = get_canonical_skill_name(raw_skill)
                if canonical:
                    found.add(canonical)

        return found

    # ---------- Matching & scoring logic ----------

    def _normalize_skill_list(self, skills: Iterable[str]) -> List[str]:
        normalized: Set[str] = set()
        for s in skills:
            if not s:
                continue
            canon = get_canonical_skill_name(s) or self._safe_title(normalize_skill(s))
            if canon:
                normalized.add(canon)
        return sorted(normalized)

    @staticmethod
    def _safe_title(text: str) -> str:
        text = (text or "").strip()
        if not text:
            return ""
        return " ".join(w.capitalize() for w in text.split())

    def _score(
        self,
        user_skills: List[str],
        required_skills: List[str],
    ) -> SkillGapReport:
        """
        Compare resume skills vs required skills and build a SkillGapReport.

        We embed *skill names* with the same sentence-transformer model and
        compute cosine similarity. This is much more robust than exact string
        comparison, especially for skills like "Object-Oriented Programming"
        vs "OOP in Python", etc.
        """
        # Deduplicate while preserving order
        user_skills = list(dict.fromkeys(user_skills))
        required_skills = list(dict.fromkeys(required_skills))

        if not required_skills or len(required_skills) < self.config.min_required_skills:
            # Not enough signal about the role – treat everything as missing.
            return SkillGapReport(
                matched_skills=[],
                partial_skills=[],
                missing_skills=required_skills,
                readiness_score=0,
                summary="Not enough job data to estimate readiness. Please add more job descriptions to the knowledge base.",
            )

        if not user_skills:
            return SkillGapReport(
                matched_skills=[],
                partial_skills=[],
                missing_skills=required_skills,
                readiness_score=0,
                summary="No skills detected in your resume. Please update your resume with your technical and professional skills.",
            )

        # Embed both sets of skills
        user_vecs = self.embedder.embed_texts(user_skills)
        req_vecs = self.embedder.embed_texts(required_skills)

        # For each required skill, find the best matching user skill
        # (max cosine similarity).
        scores, user_idx = max_similarities(req_vecs, user_vecs)

        matched: List[str] = []
        partial: List[str] = []
        missing: List[str] = []

        for req_skill, score_val, idx in zip(required_skills, scores, user_idx):
            if score_val >= self.config.match_threshold:
                matched.append(req_skill)
            elif score_val >= self.config.partial_threshold:
                partial.append(req_skill)
            else:
                missing.append(req_skill)

        # Readiness score: full weight for matched skills, partial weight for partial skills.
        total = len(required_skills)
        if total == 0:
            readiness = 0
        else:
            raw = (len(matched) + self.config.partial_weight * len(partial)) / total
            readiness = int(round(max(0.0, min(1.0, raw)) * 100))

        summary = self._build_summary(readiness, matched, partial, missing)

        return SkillGapReport(
            matched_skills=sorted(matched),
            partial_skills=sorted(partial),
            missing_skills=sorted(missing),
            readiness_score=readiness,
            summary=summary,
        )

    def _build_summary(
        self,
        readiness: int,
        matched: Sequence[str],
        partial: Sequence[str],
        missing: Sequence[str],
    ) -> str:
        """
        Simple human-readable explanation of the readiness score.
        """
        if readiness >= 80:
            base = "You are highly aligned with this role."
        elif readiness >= 60:
            base = "You meet most core requirements but have some gaps."
        elif readiness >= 40:
            base = "You cover some fundamentals but need to strengthen several important areas."
        else:
            base = "You currently lack many of the key skills for this role."

        details: List[str] = [base]

        if matched:
            details.append(f"Strong areas: {', '.join(matched[:5])}{'...' if len(matched) > 5 else ''}.")
        if partial:
            details.append(f"Partially covered: {', '.join(partial[:5])}{'...' if len(partial) > 5 else ''}.")
        if missing:
            details.append(f"Priority gaps: {', '.join(missing[:5])}{'...' if len(missing) > 5 else ''}.")

        return " ".join(details)


def build_default_skill_gap_analyzer() -> SkillGapAnalyzer:
    """
    Convenience constructor that:
    - Loads/builds the default knowledge base
    - Creates a SkillGapAnalyzer on top of it

    This can be used later in API routes or background jobs without
    duplicating setup code.
    """
    store = build_default_kb()
    analyzer = SkillGapAnalyzer(store=store)
    return analyzer


if __name__ == "__main__":
    # Minimal CLI test (assumes you have populated backend/data/jobs with at least a few job descriptions)
    demo_resume = {"skills": ["Python", "SQL", "AWS"]}
    analyzer = build_default_skill_gap_analyzer()
    report = analyzer.analyze(demo_resume, target_role="Machine Learning Engineer", top_k_jobs=10)
    import json as _json

    print(_json.dumps(report.to_dict(), indent=2, ensure_ascii=False))

