from pathlib import Path

import pytest
from docx import Document
from pypdf import PdfWriter
from pypdf.generic import DecodedStreamObject, DictionaryObject, NameObject

from utils.extract_content import extract_content

ROOT = Path(__file__).resolve().parents[1]
RESUMES = ROOT / "samples" / "resumes"


def _write_pdf(path: Path, pages: list[str | None]) -> None:
    writer = PdfWriter()
    for text in pages:
        page = writer.add_blank_page(width=300, height=300)
        if not text:
            continue
        stream = DecodedStreamObject()
        escaped = text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
        stream.set_data(f"BT /F1 24 Tf 40 150 Td ({escaped}) Tj ET".encode())
        content_ref = writer._add_object(stream)
        font_ref = writer._add_object(
            DictionaryObject(
                {
                    NameObject("/Type"): NameObject("/Font"),
                    NameObject("/Subtype"): NameObject("/Type1"),
                    NameObject("/BaseFont"): NameObject("/Helvetica"),
                }
            )
        )
        page[NameObject("/Resources")] = DictionaryObject(
            {NameObject("/Font"): DictionaryObject({NameObject("/F1"): font_ref})}
        )
        page[NameObject("/Contents")] = content_ref
    writer.write(path)


def test_txt_joins_lines_with_an_extra_newline(tmp_path):
    path = tmp_path / "resume.txt"
    path.write_text("Ada\nLovelace\n", encoding="utf-8")

    assert extract_content(path) == "Ada\n\nLovelace\n"


def test_txt_without_a_trailing_newline_is_returned_as_is(tmp_path):
    path = tmp_path / "resume.txt"
    path.write_text("Ada", encoding="utf-8")

    assert extract_content(path) == "Ada"


def test_empty_txt_returns_an_empty_string(tmp_path):
    path = tmp_path / "empty.txt"
    path.write_text("", encoding="utf-8")

    assert extract_content(path) == ""


def test_txt_reader_rejects_non_utf8(tmp_path):
    path = tmp_path / "latin1.txt"
    path.write_bytes("café".encode("latin-1"))

    with pytest.raises(UnicodeDecodeError):
        extract_content(path)


def test_docx_skips_blank_paragraphs_and_ignores_tables(tmp_path):
    path = tmp_path / "resume.docx"
    document = Document()
    document.add_paragraph("Ada Lovelace")
    document.add_paragraph("")
    document.add_paragraph("Mathematician")
    document.add_table(rows=1, cols=1).cell(0, 0).text = "Hidden in a table"
    document.save(path)

    content = extract_content(path)

    assert content == "Ada Lovelace\nMathematician\n"
    assert "Hidden in a table" not in content


def test_doc_extension_uses_the_docx_reader(tmp_path):
    docx_path = tmp_path / "resume.docx"
    document = Document()
    document.add_paragraph("Legacy name")
    document.save(docx_path)
    doc_path = tmp_path / "resume.doc"
    doc_path.write_bytes(docx_path.read_bytes())

    assert extract_content(doc_path) == "Legacy name\n"


def test_pdf_concatenates_pages_and_skips_blank_ones(tmp_path):
    path = tmp_path / "resume.pdf"
    _write_pdf(path, ["Hello PDF", None, "Second page"])

    assert extract_content(path) == "Hello PDF\nSecond page\n"


def test_blank_pdf_returns_an_empty_string(tmp_path):
    path = tmp_path / "blank.pdf"
    writer = PdfWriter()
    writer.add_blank_page(width=200, height=200)
    writer.write(path)

    assert extract_content(path) == ""


def test_sample_pdf_and_docx_yield_the_candidate_names():
    pdf = extract_content(RESUMES / "abhay resume new - Abhay Singh.pdf")
    docx = extract_content(RESUMES / "Resume for Freshers - Priyanshu Singh.docx")

    assert "Abhay Pratap Singh" in pdf
    assert "PRIYANSHU SINGH" in docx


def test_unsupported_and_uppercase_suffixes_are_rejected(tmp_path):
    markdown = tmp_path / "notes.md"
    markdown.write_text("# no", encoding="utf-8")
    pdf = tmp_path / "resume.PDF"
    _write_pdf(pdf, ["Hello PDF"])

    with pytest.raises(ValueError, match=r"Unsupported file type: \.md"):
        extract_content(markdown)
    with pytest.raises(ValueError, match=r"Unsupported file type: \.PDF"):
        extract_content(pdf)


def test_missing_file_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        extract_content(tmp_path / "missing.txt")
