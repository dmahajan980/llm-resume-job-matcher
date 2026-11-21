from llm.client import LLMClient
from schemas.job_description import JobDescription
from schemas.resume.comparison_result import ComparisonResult
from schemas.resume.resume import Resume


def evaluate_resume(
    job_description: JobDescription, resume: Resume
) -> ComparisonResult:
    """
    Evaluate the candidate's resume based on the job description.
    """
    inference_model = "openai/gpt-oss-120b"

    system_prompt = f"""
    You are an expert HR recruiter.

    Your job is to compare the candidate's resume with the job description.

    Return ONLY valid JSON matching the following schema:

    {ComparisonResult.model_json_schema()}

    IMPORTANT:
    - The candidate's name is the name of the candidate in the resume.
    - The overall score is a number between 0 and 100.
    - The strengths are the strengths of the candidate in relation to the job description.
    - The weaknesses are the weaknesses of the candidate in relation to the job description.
    - The decision reasoning is the reasoning for the overall score, verdict, strengths, and weaknesses.
    """

    user_prompt = f"""
    Compare the candidate's resume with the job description and return the comparison result.

    JOB DESCRIPTION:
    {job_description.model_dump_json(indent=2)}

    CANDIDATE'S RESUME:
    {resume.model_dump_json(indent=2)}
    """

    response = LLMClient(model=inference_model).chat(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
    )

    comparison_result = ComparisonResult.model_validate_json(response.content)
    return comparison_result
