from pydantic import BaseModel


class Project(BaseModel):
    name: str
    description: str
    technologies: list[str]
    links: list[str]
