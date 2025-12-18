"""
PDF parser for extracting text from CV PDFs.
"""

import pypdf
from pathlib import Path


class PDFParser:
    """Parse PDF files and extract text content."""

    @staticmethod
    def extract_text(pdf_path: str) -> str:
        """
        Extract text content from a PDF file.

        Args:
            pdf_path: Path to the PDF file

        Returns:
            Extracted text content

        Raises:
            FileNotFoundError: If PDF file doesn't exist
            ValueError: If file is not a PDF or is corrupted
        """
        path = Path(pdf_path)

        if not path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")

        if path.suffix.lower() != ".pdf":
            raise ValueError(f"File is not a PDF: {pdf_path}")

        try:
            with open(pdf_path, "rb") as file:
                pdf_reader = pypdf.PdfReader(file)

                if len(pdf_reader.pages) == 0:
                    raise ValueError("PDF file is empty")

                text_parts = []
                for page in pdf_reader.pages:
                    text = page.extract_text()
                    if text:
                        text_parts.append(text)

                full_text = "\n".join(text_parts)

                if not full_text.strip():
                    raise ValueError("No text could be extracted from PDF")

                return full_text

        except Exception as e:
            if isinstance(e, (FileNotFoundError, ValueError)):
                raise
            raise ValueError(f"Error reading PDF file: {str(e)}")

    @staticmethod
    def extract_metadata(pdf_path: str) -> dict:
        """
        Extract metadata from a PDF file.

        Args:
            pdf_path: Path to the PDF file

        Returns:
            Dictionary containing PDF metadata
        """
        try:
            with open(pdf_path, "rb") as file:
                pdf_reader = pypdf.PdfReader(file)
                metadata = pdf_reader.metadata or {}

                return {
                    "title": metadata.get("/Title", ""),
                    "author": metadata.get("/Author", ""),
                    "subject": metadata.get("/Subject", ""),
                    "creator": metadata.get("/Creator", ""),
                    "producer": metadata.get("/Producer", ""),
                    "pages": len(pdf_reader.pages),
                }
        except Exception:
            return {}
