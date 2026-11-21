from enum import Enum
from pydantic import BaseModel


class Verdict(Enum):
    STRONG_MATCH = "Strong Match"
    GOOD_MATCH = "Good Match"
    NEUTRAL = "Neutral"
    POOR_MATCH = "Poor Match"
    STRONGLY_POOR_MATCH = "Strongly Poor Match"


class ComparisonResult(BaseModel):
    candidate_name: str
    overall_score: float
    verdict: Verdict
    strengths: list[str]
    weaknesses: list[str]
    decision_reasoning: str
