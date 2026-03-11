"""
Job Recommendation Engine (Module 5)

This module uses RAG principles:
- Retrieve semantically relevant job descriptions from the FAISS vector store
- Match against resume skills with embeddings (not keyword matching)
- Rank + explain results for transparent recommendations
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

from .skill_database import SKILL_DATABASE, get_canonical_skill_name, normalize_skill
from .vector_store import FaissVectorStore, build_default_kb
from embeddings.embedder import Embedder
from models.job_match import JobMatch
from models.skill_report import SkillGapReport
from utils.ranker import JobRanker, RankerConfig


@dataclass
class JobPreferences:
    domain: Optional[str] = None
    experience_level: Optional[str] = None  # e.g., "entry", "mid", "senior"


@dataclass
class JobRecommenderConfig:
    # Retrieval scope
    top_k_retrieval: int = 25
    # Minimum semantic similarity to keep a job (0..1)
    similarity_threshold: float = 0.15
    # Minimum required skills extracted from a job to consider it valid
    min_required_skills: int = 3
    # Default number of jobs to return
    max_jobs: int = 5


class JobRecommender:
    """
    End-to-end job recommendation pipeline.

    Responsibilities:
    - Retrieval from FAISS (RAG-style)
    - Skill extraction from job descriptions
    - Ranking & explanation via JobRanker
    """

    def __init__(
        self,
        store: FaissVectorStore,
        embedder: Optional[Embedder] = None,
        config: Optional[JobRecommenderConfig] = None,
        ranker_config: Optional[RankerConfig] = None,
    ):
        self.store = store
        self.embedder = embedder or store.embedder
        self.config = config or JobRecommenderConfig()
        self.ranker = JobRanker(self.embedder, ranker_config)

    def recommend_jobs(
        self,
        resume_json: Dict,
        *,
        skill_gap_report: Optional[SkillGapReport | Dict] = None,
        preferences: Optional[JobPreferences] = None,
        top_n: Optional[int] = None,
        similarity_threshold: Optional[float] = None,
    ) -> Dict:
        """
        Generate job recommendations for a user.

        Args:
            resume_json: Parsed resume JSON (expects "skills").
            skill_gap_report: SkillGapReport from Module 4 (optional).
            preferences: Optional domain and experience level filters.
            top_n: Override number of jobs returned.
            similarity_threshold: Override similarity threshold.
        """
        preferences = preferences or JobPreferences()
        report = self._coerce_skill_gap_report(skill_gap_report)

        resume_skills = self._normalize_skill_list(resume_json.get("skills") or [])
        resume_summary = self._build_resume_summary(resume_skills, report, preferences)

        # If vector store is empty, return empty results immediately
        if len(self.store) == 0:
            return {"recommended_jobs": []}
        
        # Try to search, but handle timeouts gracefully
        try:
            query = self._build_query(resume_skills, preferences)
            search_result = self.store.search(query, top_k=self.config.top_k_retrieval)
            results = search_result.get("results", [])
        except Exception as e:
            # If search fails (e.g., embedder not ready), return empty
            print(f"Warning: Search failed in job recommender: {e}")
            return {"recommended_jobs": []}

        # Prefer job-tagged chunks; fall back to all if missing.
        job_chunks = [r for r in results if r.get("source") == "job"]
        if not job_chunks:
            job_chunks = results

        aggregated = self._aggregate_job_chunks(job_chunks)

        threshold = similarity_threshold if similarity_threshold is not None else self.config.similarity_threshold
        max_jobs = top_n if top_n is not None else self.config.max_jobs

        recommendations: List[Tuple[JobMatch, float, float]] = []
        for doc_id, job_text, best_score, tag in aggregated:
            if preferences.domain and not self._matches_domain(job_text, doc_id, tag, preferences.domain):
                continue
            if preferences.experience_level and not self._matches_experience(job_text, doc_id, preferences.experience_level):
                continue

            job_skills = self._extract_skills_from_text(job_text)
            if len(job_skills) < self.config.min_required_skills:
                continue

            rank = self.ranker.rank_job(
                resume_skills=resume_skills,
                job_skills=job_skills,
                resume_summary=resume_summary,
                job_text=job_text,
                skill_gap_report=report,
            )

            if rank.semantic_score < threshold and rank.coverage_score < 0.2:
                continue

            job_title = self._infer_job_title(doc_id, job_text)

            recommendations.append(
                (
                    JobMatch(
                        job_title=job_title,
                        match_score=rank.match_score,
                        matched_skills=sorted(rank.matched_skills),
                        missing_skills=sorted(rank.missing_skills),
                        reason=rank.reason,
                    ),
                    rank.match_score,
                    best_score,
                )
            )

        # Sort by match score, then by retrieval similarity score
        recommendations.sort(key=lambda x: (x[1], x[2]), reverse=True)
        top_jobs = [r[0].to_dict() for r in recommendations[:max_jobs]]

        return {"recommended_jobs": top_jobs}

    # ---------- Retrieval helpers ----------

    def _build_query(self, resume_skills: Sequence[str], preferences: JobPreferences) -> str:
        """
        Build a retrieval query for FAISS.

        RAG benefit: this query is embedded and matched by meaning,
        so we can retrieve relevant jobs even without exact keyword overlap.
        """
        parts: List[str] = ["job description", "requirements"]
        if preferences.domain:
            parts.append(preferences.domain)
        if preferences.experience_level:
            parts.append(f"{preferences.experience_level} level")
        if resume_skills:
            parts.append("skills: " + ", ".join(resume_skills[:15]))
        return " ".join(parts)

    def _aggregate_job_chunks(
        self,
        job_chunks: Sequence[Dict],
    ) -> List[Tuple[str, str, float, Optional[str]]]:
        """
        Group chunk results by document_id and combine them.

        Returns tuples of (doc_id, combined_text, best_score, tag).
        """
        grouped: Dict[str, Dict] = {}
        for item in job_chunks:
            metadata = item.get("metadata") or {}
            doc_id = metadata.get("document_id") or f"job_{len(grouped) + 1}"
            tag = metadata.get("tag")

            if doc_id not in grouped:
                grouped[doc_id] = {
                    "contents": [],
                    "best_score": float(item.get("score", 0.0)),
                    "tag": tag,
                }

            grouped[doc_id]["contents"].append(item.get("content") or "")
            grouped[doc_id]["best_score"] = max(grouped[doc_id]["best_score"], float(item.get("score", 0.0)))

        aggregated: List[Tuple[str, str, float, Optional[str]]] = []
        for doc_id, payload in grouped.items():
            contents = [c for c in payload["contents"] if c]
            # Deduplicate while preserving order
            merged = "\n".join(dict.fromkeys(contents))
            aggregated.append((doc_id, merged, payload["best_score"], payload["tag"]))

        return aggregated

    # ---------- Skill extraction helpers ----------

    def _extract_skills_from_text(self, text: str) -> List[str]:
        if not text:
            return []

        text_lower = text.lower()
        found: List[str] = []

        for raw_skill in SKILL_DATABASE:
            pattern = r"\b" + raw_skill.replace("+", r"\+") + r"\b"
            if __import__("re").search(pattern, text_lower):
                canonical = get_canonical_skill_name(raw_skill)
                if canonical and canonical not in found:
                    found.append(canonical)

        return found

    def _normalize_skill_list(self, skills: Iterable[str]) -> List[str]:
        normalized: List[str] = []
        for s in skills:
            if not s:
                continue
            canon = get_canonical_skill_name(s)
            if not canon:
                canon = self._safe_title(normalize_skill(s))
            if canon and canon not in normalized:
                normalized.append(canon)
        return normalized

    @staticmethod
    def _safe_title(text: str) -> str:
        text = (text or "").strip()
        if not text:
            return ""
        return " ".join(w.capitalize() for w in text.split())

    # ---------- Filters ----------

    def _matches_domain(self, job_text: str, doc_id: str, tag: Optional[str], domain: str) -> bool:
        domain_norm = (domain or "").strip().lower()
        if not domain_norm:
            return True

        haystacks = [
            (job_text or "").lower(),
            (doc_id or "").lower(),
            (tag or "").lower(),
        ]
        return any(domain_norm in h for h in haystacks)

    def _matches_experience(self, job_text: str, doc_id: str, experience_level: str) -> bool:
        level = (experience_level or "").strip().lower()
        if not level:
            return True

        keywords = {
            "intern": ["intern", "internship", "trainee"],
            "entry": ["entry", "junior", "graduate", "fresher", "associate"],
            "mid": ["mid", "intermediate", "mid-level"],
            "senior": ["senior", "lead", "principal", "staff"],
        }

        haystack = f"{doc_id}\n{job_text}".lower()
        terms = keywords.get(level, [level])
        return any(term in haystack for term in terms)

    # ---------- Explanation helpers ----------

    def _build_resume_summary(
        self,
        resume_skills: Sequence[str],
        report: Optional[SkillGapReport],
        preferences: JobPreferences,
    ) -> str:
        """
        Build a concise resume summary for semantic similarity scoring.
        """
        parts: List[str] = []
        if resume_skills:
            parts.append("Skills: " + ", ".join(resume_skills[:20]))
        if report:
            if report.matched_skills:
                parts.append("Strengths: " + ", ".join(report.matched_skills[:10]))
            if report.missing_skills:
                parts.append("Gaps: " + ", ".join(report.missing_skills[:10]))
        if preferences.domain:
            parts.append(f"Target domain: {preferences.domain}")
        if preferences.experience_level:
            parts.append(f"Experience level: {preferences.experience_level}")
        return ". ".join(parts)

    def _infer_job_title(self, doc_id: str, job_text: str) -> str:
        if doc_id:
            name = Path(doc_id).stem
            name = name.replace("_", " ").replace("-", " ").strip()
            if name:
                return self._safe_title(name)

        if job_text:
            first_line = job_text.strip().splitlines()[0][:80]
            if first_line:
                return first_line.strip()

        return "Job Role"

    @staticmethod
    def _coerce_skill_gap_report(report: Optional[SkillGapReport | Dict]) -> Optional[SkillGapReport]:
        if report is None:
            return None
        if isinstance(report, SkillGapReport):
            return report
        if isinstance(report, dict):
            return SkillGapReport(
                matched_skills=report.get("matched_skills") or [],
                partial_skills=report.get("partial_skills") or [],
                missing_skills=report.get("missing_skills") or [],
                readiness_score=int(report.get("readiness_score") or 0),
                summary=report.get("summary") or "",
            )
        return None


def build_default_job_recommender() -> JobRecommender:
    """
    Convenience constructor that:
    - Builds/loads the default vector store KB
    - Returns a ready-to-use JobRecommender
    """
    store = build_default_kb()
    return JobRecommender(store=store)


if __name__ == "__main__":
    # Simple evaluation example (requires backend/data/jobs to be populated)
    demo_resume = {"skills": ["Python", "SQL", "AWS", "Pandas"]}
    recommender = build_default_job_recommender()
    result = recommender.recommend_jobs(
        demo_resume,
        skill_gap_report=None,
        preferences=JobPreferences(domain="data", experience_level="entry"),
        top_n=3,
    )
    import json as _json

    print(_json.dumps(result, indent=2, ensure_ascii=False))
