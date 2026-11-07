import json
import os
from dotenv import load_dotenv
from groq import Groq
from pathlib import Path
from schemas import job_description
from schemas.job_description import JobDescription


load_dotenv()
LLM_API_KEY = os.getenv("GROQ_API_KEY")

if not LLM_API_KEY:
    raise ValueError("GROQ_API_KEY is not set")

llm_client = Groq(api_key=LLM_API_KEY)
model = "openai/gpt-oss-20b"


########################################################
# Structured job description extraction
########################################################
job_description_content = Path("samples/job_description.md").read_text()
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

response = llm_client.chat.completions.create(
    model=model,
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ],
    response_format={"type": "json_object"},
)

job_description_raw_json = response.choices[0].message.content
job_description = JobDescription.model_validate_json(job_description_raw_json)

print(job_description.model_dump_json(indent=2))
