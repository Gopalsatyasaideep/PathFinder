"""
Learning step model for Module 7 (Personalized Learning Path Generator).
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Dict, List, Optional


@dataclass
class LearningStep:
    phase: str
    skill: str
    resources: List[str] = field(default_factory=list)
    outcome: str = ""
    difficulty: Optional[str] = None
    estimated_weeks: Optional[int] = None

    def to_dict(self) -> Dict:
        """Return a JSON-serializable dict."""
        return asdict(self)
