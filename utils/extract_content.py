from pathlib import Path


def extract_content(path: Path) -> str:
    """
    Extract the content of a file.
    Supported file types: .pdf, .docx, .doc, .txt
    """

    def extract_pdf_content(path: Path) -> str:
        """
        Extract the content of the PDF files.
        """
        from pypdf import PdfReader

        reader = PdfReader(path)
        pages = reader.pages

        _content = ""
        for page in pages:
            page_content = page.extract_text()
            if page_content:
                _content += page_content + "\n"

        return _content

    def extract_docx_content(path: Path) -> str:
        """
        Extract the content of the DOCX and DOC files.
        """
        from docx import Document

        doc = Document(path)
        paragraphs = doc.paragraphs

        _content = ""
        for paragraph in paragraphs:
            paragraph_content = paragraph.text
            if paragraph_content:
                _content += paragraph_content + "\n"

        return _content

    def extract_txt_content(path: Path) -> str:
        """
        Extract the content of the TXT files.
        """
        with path.open("r", encoding="utf-8") as file:
            _content = file.readlines()
        return "\n".join(_content)

    if path.suffix == ".pdf":
        _content = extract_pdf_content(path)
    elif path.suffix in [".docx", ".doc"]:
        _content = extract_docx_content(path)
    elif path.suffix == ".txt":
        _content = extract_txt_content(path)
    else:
        raise ValueError(f"Unsupported file type: {path.suffix}")

    return _content
