from datetime import date

import pytest
from pydantic import ValidationError

from schemas.job_description import JobDescription
from schemas.resume.comparison_result import ComparisonResult, Verdict
from schemas.resume.education import Education
from schemas.resume.experience import Experience
from schemas.resume.project import Project
from schemas.resume.resume import Resume
from tests.helpers import sample_comparison, sample_job_description, sample_resume


def test_job_description_round_trips_and_defaults_experience_to_none():
    job = JobDescription(
        role="SDE-I",
        required_skills=["Python"],
        preferred_skills=[],
        educational_qualifications=["B.Tech"],
        responsibilities=["Ship services"],
    )

    assert job.minimum_experience is None
    assert JobDescription.model_validate_json(job.model_dump_json()) == job


def test_job_description_rejects_a_missing_required_list():
    with pytest.raises(ValidationError):
        JobDescription.model_validate(
            {
                "role": "SDE-I",
                "required_skills": ["Python"],
                "preferred_skills": [],
                "educational_qualifications": [],
            }
        )


def test_resume_keeps_optional_contact_fields_empty():
    resume = sample_resume()

    assert resume.phone is None
    assert resume.certifications == []
    assert Resume.model_validate_json(resume.model_dump_json()) == resume


def test_resume_rejects_an_empty_object():
    with pytest.raises(ValidationError) as raised:
        Resume.model_validate({})

    missing = {error["loc"][0] for error in raised.value.errors()}
    assert missing == {
        "name",
        "skills",
        "certifications",
        "education",
        "experience",
        "projects",
    }


def test_education_leaves_unspecified_details_empty():
    education = Education(institution_name="SRMS", degree_name="B.Tech")

    assert education.major is None
    assert education.grade is None
    assert education.achievements is None


def test_experience_parses_iso_dates_and_rejects_prose_dates():
    experience = Experience.model_validate(
        {
            "company_name": "Codeware",
            "title": "Intern",
            "start_date": "2025-06-01",
            "end_date": None,
            "responsibilities": ["Built UI"],
            "skills": ["React"],
        }
    )

    assert experience.start_date == date(2025, 6, 1)
    assert experience.end_date is None

    with pytest.raises(ValidationError):
        Experience.model_validate(
            {
                "company_name": "Codeware",
                "title": "Intern",
                "start_date": "Jun 2025",
                "responsibilities": [],
                "skills": [],
            }
        )


def test_project_requires_every_field():
    with pytest.raises(ValidationError):
        Project(name="Converter", description="Converts currency", technologies=["React"])


@pytest.mark.parametrize(
    "verdict",
    [
        Verdict.STRONG_MATCH,
        Verdict.GOOD_MATCH,
        Verdict.NEUTRAL,
        Verdict.POOR_MATCH,
        Verdict.STRONGLY_POOR_MATCH,
    ],
)
def test_comparison_accepts_each_verdict_label(verdict):
    result = sample_comparison().model_copy(update={"verdict": verdict})

    parsed = ComparisonResult.model_validate_json(result.model_dump_json())

    assert parsed.verdict is verdict


def test_comparison_coerces_an_integer_score_and_rejects_unknown_verdicts():
    result = ComparisonResult.model_validate(
        {
            "candidate_name": "Ada Lovelace",
            "overall_score": 80,
            "verdict": "Good Match",
            "strengths": [],
            "weaknesses": [],
            "decision_reasoning": "Solid match.",
        }
    )

    assert result.overall_score == 80.0

    with pytest.raises(ValidationError):
        ComparisonResult.model_validate(
            {
                "candidate_name": "Ada Lovelace",
                "overall_score": 80,
                "verdict": "GOOD_MATCH",
                "strengths": [],
                "weaknesses": [],
                "decision_reasoning": "Solid match.",
            }
        )


def test_comparison_does_not_clamp_the_score():
    # The 0–100 range is only in the prompt. The schema stores whatever number comes back.
    result = sample_comparison().model_copy(update={"overall_score": 140})

    assert ComparisonResult.model_validate(result.model_dump()).overall_score == 140


def test_sample_job_and_resume_are_valid_models():
    assert sample_job_description().role == "SDE-I"
    assert sample_resume().name == "Ada Lovelace"
