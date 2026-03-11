"""
Data model for the Skill Gap Analysis report (Module 4).

This is kept separate from service logic so it can be:
- Serialized to JSON for APIs
- Reused by future modules (learning path, chatbot, dashboards)
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Dict, List


@dataclass
class SkillGapReport:
    matched_skills: List[str] = field(default_factory=list)
    partial_skills: List[str] = field(default_factory=list)
    missing_skills: List[str] = field(default_factory=list)
    readiness_score: int = 0
    summary: str = ""

    def to_dict(self) -> Dict:
        """Return a plain JSON-serializable dict."""
        return asdict(self)

