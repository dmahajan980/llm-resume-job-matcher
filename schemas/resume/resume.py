from typing import Optional
from schemas.resume.education import Education
from schemas.resume.experience import Experience
from schemas.resume.project import Project
from pydantic import BaseModel


class Resume(BaseModel):
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    skills: list[str]
    certifications: list[str]
    education: list[Education]
    experience: list[Experience]
    projects: list[Project]
