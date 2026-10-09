"""
tools/file_reader_tool.py
Centralised document-reading tool used by the Fact Researcher agent.
Supports: PDF (.pdf), Word (.docx), plain text (.txt)
"""

from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type
from pathlib import Path


class FileReaderInput(BaseModel):
    """Input schema for FileReaderTool."""
    file_path: str = Field(..., description="Absolute path to a PDF, DOCX, or TXT file.")


class FileReaderTool(BaseTool):
    name: str = "File Reader Tool"
    description: str = (
        "Read and extract text content from an uploaded document. "
        "Supports PDF, DOCX, and TXT formats. "
        "Provide the absolute file path to the document."
    )
    args_schema: Type[BaseModel] = FileReaderInput

    def _run(self, file_path: str) -> str:
        path = Path(file_path)

        if not path.exists():
            return f"Error: File not found at path: {file_path}"

        suffix = path.suffix.lower()

        try:
            if suffix == ".pdf":
                return self._read_pdf(path)
            elif suffix == ".docx":
                return self._read_docx(path)
            elif suffix == ".txt":
                return self._read_txt(path)
            else:
                return f"Unsupported file format: '{suffix}'. Use PDF, DOCX, or TXT."
        except Exception as e:
            return f"Error reading file '{path.name}': {str(e)}"

    # ── internal readers ──────────────────────────────────────────────────────

    def _read_pdf(self, path: Path) -> str:
        import PyPDF2
        with open(path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            text = "\n".join(page.extract_text() or "" for page in reader.pages)
        return f"PDF Content from '{path.name}':\n\n{text.strip()}"

    def _read_docx(self, path: Path) -> str:
        from docx import Document
        doc = Document(str(path))
        text = "\n".join(p.text for p in doc.paragraphs if p.text.strip())
        return f"DOCX Content from '{path.name}':\n\n{text.strip()}"

    def _read_txt(self, path: Path) -> str:
        for enc in ("utf-8", "utf-16", "latin-1", "cp1252"):
            try:
                text = path.read_text(encoding=enc)
                return f"TXT Content from '{path.name}':\n\n{text.strip()}"
            except UnicodeDecodeError:
                continue
        return f"Error: Could not decode '{path.name}' with any supported encoding."
