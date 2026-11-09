import os
from concurrent.futures import Future, ProcessPoolExecutor

import pytest
from pydantic import ValidationError

import main
from tests.helpers import (
    install_recording_client,
    sample_comparison,
    sample_job_description,
    sample_resume,
)
from utils.evaluate_resume import evaluate_resume
from utils.parse_job_description import parse_job_description
from utils.parse_resume import parse_resume


def test_evaluate_resume_scores_the_structured_records(monkeypatch):
    job = sample_job_description()
    resume = sample_resume()
    comparison = sample_comparison()
    created = install_recording_client(
        monkeypatch,
        "utils.evaluate_resume.LLMClient",
        comparison.model_dump_json(),
    )

    result = evaluate_resume(job, resume)

    assert result == comparison
    assert created[0].model == "openai/gpt-oss-120b"
    assert job.model_dump_json(indent=2) in created[0].user_prompt
    assert resume.model_dump_json(indent=2) in created[0].user_prompt
    assert "overall score is a number between 0 and 100" in created[0].system_prompt


@pytest.mark.parametrize(
    ("function", "target", "payload"),
    [
        (parse_job_description, "utils.parse_job_description.LLMClient", "not-json"),
        (parse_resume, "utils.parse_resume.LLMClient", "```json\n{}\n```"),
        (
            lambda text: evaluate_resume(sample_job_description(), sample_resume()),
            "utils.evaluate_resume.LLMClient",
            "null",
        ),
    ],
)
def test_parsers_reject_responses_that_are_not_the_schema(
    monkeypatch, function, target, payload
):
    install_recording_client(monkeypatch, target, payload)

    with pytest.raises(ValidationError):
        function("content")


def test_read_and_evaluate_resume_chains_extract_parse_and_score(monkeypatch, tmp_path):
    path = tmp_path / "ada.txt"
    job = sample_job_description()
    resume = sample_resume()
    comparison = sample_comparison()
    calls = []

    monkeypatch.setattr(
        main,
        "extract_content",
        lambda file_path: calls.append(("extract", file_path)) or "raw",
    )
    monkeypatch.setattr(
        main, "parse_resume", lambda content: calls.append(("parse", content)) or resume
    )
    monkeypatch.setattr(
        main,
        "evaluate_resume",
        lambda job_description, parsed: calls.append(("score", job_description, parsed))
        or comparison,
    )

    assert main.read_and_evaluate_resume(job, path) is comparison
    assert calls == [("extract", path), ("parse", "raw"), ("score", job, resume)]


def test_read_and_evaluate_resume_wraps_failures_as_a_picklable_runtime_error(
    monkeypatch, tmp_path
):
    def explode(path):
        raise ValueError("unreadable")

    monkeypatch.setattr(main, "extract_content", explode)

    with pytest.raises(RuntimeError, match="unreadable") as raised:
        main.read_and_evaluate_resume(sample_job_description(), tmp_path / "ada.pdf")

    assert raised.value.__cause__ is None


def test_worker_error_survives_the_process_pool(tmp_path):
    resume = tmp_path / "notes.xyz"
    resume.write_text("not a resume", encoding="utf-8")

    with ProcessPoolExecutor(max_workers=1) as executor:
        future = executor.submit(
            main.read_and_evaluate_resume, sample_job_description(), resume
        )
        with pytest.raises(RuntimeError, match=r"Unsupported file type: \.xyz"):
            future.result()


def test_main_scores_every_directory_entry_and_prints_results(
    monkeypatch, tmp_path, capsys
):
    monkeypatch.chdir(tmp_path)
    resumes = tmp_path / "samples" / "resumes"
    resumes.mkdir(parents=True)
    (tmp_path / "samples" / "job_description.md").write_text(
        "SDE posting", encoding="utf-8"
    )
    (resumes / "ada.txt").write_text("ada", encoding="utf-8")
    (resumes / "grace.docx").write_text("grace", encoding="utf-8")

    job = sample_job_description()
    submitted = {}

    class Executor:
        def __init__(self, max_workers):
            assert max_workers == main.MAX_PROCESSING_UNITS

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def submit(self, fn, job_description, path):
            assert fn is main.read_and_evaluate_resume
            submitted[path.name] = job_description
            future = Future()
            future.set_result(f"scored {path.name}")
            return future

    monkeypatch.setattr(
        main,
        "parse_job_description",
        lambda text: job if text == "SDE posting" else None,
    )
    monkeypatch.setattr(main, "ProcessPoolExecutor", Executor)

    main.main()

    output = capsys.readouterr().out
    assert "ada.txt: scored ada.txt" in output
    assert "grace.docx: scored grace.docx" in output
    assert submitted == {"ada.txt": job, "grace.docx": job}


def test_main_lets_a_worker_failure_surface(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    resumes = tmp_path / "samples" / "resumes"
    resumes.mkdir(parents=True)
    (tmp_path / "samples" / "job_description.md").write_text(
        "SDE posting", encoding="utf-8"
    )
    (resumes / "ada.txt").write_text("ada", encoding="utf-8")

    class Executor:
        def __init__(self, max_workers):
            pass

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def submit(self, fn, job_description, path):
            future = Future()
            future.set_exception(RuntimeError("token limit"))
            return future

    monkeypatch.setattr(
        main, "parse_job_description", lambda text: sample_job_description()
    )
    monkeypatch.setattr(main, "ProcessPoolExecutor", Executor)

    with pytest.raises(RuntimeError, match="token limit"):
        main.main()


def test_worker_cap_is_two():
    assert main.MAX_PROCESSING_UNITS == min(os.cpu_count(), 2)
    assert 1 <= main.MAX_PROCESSING_UNITS <= 2
