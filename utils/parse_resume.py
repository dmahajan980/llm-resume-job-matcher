from llm.client import LLMClient
from schemas.resume.resume import Resume


def parse_resume(resume_content: str) -> Resume:
    resume_schema = Resume.model_json_schema()

    system_prompt = f"""
    You are an expert resume parser.

    Your job is to extract structured information from the resume.
    Different resumes may use different headings.

    For example:
    - Experience
    - Professional Experience
    - Work History
    - Employment
    - Internships

    These may all contain relevant experience.

    Skills may also appear in the skills section, work experience,
    internships or projects.

    Return ONLY valid JSON matching this schema:

    ```json
    {resume_schema}
    ```

    IMPORTANT:
    - Do not invent information. Fill the schema with actual information extracted from the resume.
    - If information for a list is missing, return an empty list for the corresponding field.
    - If a value is not available, return null.
    - Include internships inside experiences.
    - Extract skills mentioned across the entire resume.
    """

    user_prompt = f"""
    Analyze the following resume and extract structured information from it:

    ```
    {resume_content}
    ```
    """

    response = LLMClient(model="openai/gpt-oss-120b").chat(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
    )

    resume = Resume.model_validate_json(response.content)
    return resume
