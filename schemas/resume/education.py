from typing import Optional
from pydantic import BaseModel


class Education(BaseModel):
    institution_name: str
    degree_name: str
    major: str
    grade: float
    start_year: int
    end_year: int
    description: str
    achievements: Optional[list[str]] = None
