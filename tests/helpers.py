from datetime import date
from types import SimpleNamespace

from schemas.job_description import JobDescription
from schemas.resume.comparison_result import ComparisonResult, Verdict
from schemas.resume.education import Education
from schemas.resume.experience import Experience
from schemas.resume.project import Project
from schemas.resume.resume import Resume


def sample_job_description() -> JobDescription:
    return JobDescription(
        role="SDE-I",
        required_skills=["Python"],
        preferred_skills=["AWS"],
        minimum_experience=0,
        educational_qualifications=["B.Tech"],
        responsibilities=["Ship services"],
    )


def sample_resume() -> Resume:
    return Resume(
        name="Ada Lovelace",
        email="ada@example.com",
        phone=None,
        skills=["Python"],
        certifications=[],
        education=[
            Education(
                institution_name="Analytical Engines",
                degree_name="Mathematics",
                start_year=1835,
            )
        ],
        experience=[
            Experience(
                company_name="Difference Engine",
                title="Programmer",
                start_date=date(1842, 1, 1),
                responsibilities=["Wrote notes"],
                skills=["Algorithms"],
            )
        ],
        projects=[
            Project(
                name="Note G",
                description="First algorithm",
                technologies=["Mathematics"],
                links=[],
            )
        ],
    )


def sample_comparison() -> ComparisonResult:
    return ComparisonResult(
        candidate_name="Ada Lovelace",
        overall_score=88,
        verdict=Verdict.GOOD_MATCH,
        strengths=["Algorithms"],
        weaknesses=["No cloud experience"],
        decision_reasoning="Strong fundamentals, missing the preferred stack.",
    )


class RecordingClient:
    """Stand-in for LLMClient. Records the prompt and returns canned JSON."""

    def __init__(self, model: str = "openai/gpt-oss-20b"):
        self.model = model
        self.system_prompt = None
        self.user_prompt = None
        self.messages = None
        self.content = "{}"

    def chat(self, system_prompt, user_prompt, messages=None):
        self.system_prompt = system_prompt
        self.user_prompt = user_prompt
        self.messages = messages
        return SimpleNamespace(content=self.content)


def install_recording_client(monkeypatch, target: str, content: str) -> list:
    created = []

    def factory(model: str = "openai/gpt-oss-20b"):
        client = RecordingClient(model)
        client.content = content
        created.append(client)
        return client

    monkeypatch.setattr(target, factory)
    return created
