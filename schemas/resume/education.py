from typing import Optional
from pydantic import BaseModel


class Education(BaseModel):
    institution_name: str
    degree_name: str
    major: Optional[str] = None
    grade: Optional[float] = None
    start_year: Optional[int] = None
    end_year: Optional[int] = None
    description: Optional[str] = None
    achievements: Optional[list[str]] = None
