from datetime import date
from typing import Optional
from pydantic import BaseModel


class Experience(BaseModel):
    company_name: str
    title: str
    start_date: date
    end_date: Optional[date] = None
    responsibilities: list[str]
    skills: list[str]
