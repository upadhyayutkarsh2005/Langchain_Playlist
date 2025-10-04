# features/document_qa/loader.py
import os
from pathlib import Path
from typing import List
from uuid import uuid4

import PyPDF2

UPLOAD_DIR = Path("data/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

def save_upload(file_obj, filename: str) -> str:
    """
    Save an uploaded file-like object to disk and return saved path.
    `file_obj` supports .read() (FastAPI UploadFile.file).
    """
    unique_name = f"{uuid4().hex}_{filename}"
    saved_path = UPLOAD_DIR / unique_name
    with open(saved_path, "wb") as f:
        f.write(file_obj.read())
    return str(saved_path)

def extract_text_from_pdf(path: str) -> str:
    """
    Extracts text from a PDF using PyPDF2.
    Returns a single large string with the PDF content.
    """
    text_chunks: List[str] = []
    with open(path, "rb") as fh:
        reader = PyPDF2.PdfReader(fh)
        for page in reader.pages:
            try:
                text = page.extract_text() or ""
            except Exception:
                text = ""
            if text:
                text_chunks.append(text)
    return "\n\n".join(text_chunks)