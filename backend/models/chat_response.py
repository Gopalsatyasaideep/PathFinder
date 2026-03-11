"""
Chat response model for Module 6 (AI Career Assistant).

Keeps FastAPI responses consistent and JSON-serializable.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Dict, List, Optional


@dataclass
class ChatResponse:
    question: str
    answer: str
    sources: List[str] = field(default_factory=list)
    confidence: Optional[float] = None

    def to_dict(self) -> Dict:
        """Return a JSON-serializable dict."""
        return asdict(self)
