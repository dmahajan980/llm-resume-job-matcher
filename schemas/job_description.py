from pydantic import BaseModel
from typing import Optional


class JobDescription(BaseModel):
    role: str
    required_skills: list[str]
    preferred_skills: list[str]
    minimum_experience: Optional[int] = None
    educational_qualifications: list[str]
    responsibilities: list[str]
