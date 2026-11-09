import os
from concurrent.futures import as_completed, ProcessPoolExecutor
from pathlib import Path
from schemas.job_description import JobDescription
from schemas.resume.comparison_result import ComparisonResult
from utils.evaluate_resume import evaluate_resume
from utils.parse_job_description import parse_job_description
from utils.parse_resume import parse_resume
from utils.extract_content import extract_content


MAX_PROCESSING_UNITS = min(os.cpu_count(), 2)


def read_and_evaluate_resume(
    job_description: JobDescription, resume_file_path: Path
) -> ComparisonResult:
    try:
        resume_content = extract_content(resume_file_path)
        resume = parse_resume(resume_content)
        return evaluate_resume(job_description, resume)
    except Exception as error:
        # Groq's APIStatusError cannot be pickled back to the parent process.
        raise RuntimeError(str(error)) from None


def main() -> None:
    # Structured job description extraction
    job_description_content = Path("samples/job_description.md").read_text()
    job_description = parse_job_description(job_description_content)

    # Resume scoring
    resume_directory = Path("samples/resumes")
    resume_processing_futures = {}

    with ProcessPoolExecutor(max_workers=MAX_PROCESSING_UNITS) as executor:
        for resume_file_path in resume_directory.iterdir():
            resume_processing_futures[
                executor.submit(
                    read_and_evaluate_resume, job_description, resume_file_path
                )
            ] = resume_file_path.name

    for future in as_completed(resume_processing_futures):
        print(f"{resume_processing_futures[future]}: {future.result()}")


if __name__ == "__main__":
    main()
