"""
Job Match model for Module 5 (Job Recommendation Engine).

This model keeps the response format consistent and JSON-serializable
for FastAPI integration.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Dict, List


@dataclass
class JobMatch:
    job_title: str
    match_score: int
    matched_skills: List[str] = field(default_factory=list)
    missing_skills: List[str] = field(default_factory=list)
    reason: str = ""

    def to_dict(self) -> Dict:
        """Return a JSON-serializable dict."""
        return asdict(self)
