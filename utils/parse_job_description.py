from llm.client import LLMClient
from schemas.job_description import JobDescription


def parse_job_description(job_description_content: str) -> JobDescription:
    job_description_schema = JobDescription.model_json_schema()

    system_prompt = f"""
    You are an expert HR assistant.

    Your job is to analyze job descriptions and extract
    structured information from them.

    Return ONLY valid JSON matching this schema:

    {job_description_schema}

    IMPORTANT:
    - Do not invent information. Fill the schema with actual information extracted from the job description.
    - If minimum experience is not mentioned, return null for the corresponding field.
    - If information for a list is missing, return an empty list for the corresponding field.
    """

    user_prompt = f"""
    Analyze the following job description and extract structured information from it.

    {job_description_content}
    """

    response = LLMClient().chat(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
    )

    job_description = JobDescription.model_validate_json(response.content)
    return job_description
