import os
from pathlib import Path
from PIL import Image
import pytesseract
import pypdf
from docx import Document

pytesseract.pytesseract.tesseract_cmd = os.getenv("TESSERACT_PATH", "tesseract")

SUPPORTED_EXTENSIONS = {".txt", ".md", ".pdf", ".docx", ".png", ".jpg", ".jpeg", ".webp"}


def clean_text(text: str) -> str:
    """Remove null bytes and extra whitespace."""
    text = text.replace("\x00", "")
    text = "\n".join(line for line in text.splitlines() if line.strip())
    return text.strip()


def load_document(file_path: str) -> str:
    path = Path(file_path)
    ext  = path.suffix.lower()

    if ext not in SUPPORTED_EXTENSIONS:
        raise ValueError(f"Unsupported file type: {ext}")

    if ext in {".txt", ".md"}:
        return clean_text(_load_text(path))
    elif ext == ".pdf":
        return clean_text(_load_pdf(path))
    elif ext == ".docx":
        return clean_text(_load_docx(path))
    elif ext in {".png", ".jpg", ".jpeg", ".webp"}:
        return clean_text(_load_image(path))


def _load_text(path: Path) -> str:
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()


def _load_pdf(path: Path) -> str:
    text = ""
    with open(path, "rb") as f:
        reader = pypdf.PdfReader(f)
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text


def _load_docx(path: Path) -> str:
    doc = Document(path)
    return "\n".join([para.text for para in doc.paragraphs if para.text.strip()])


def _load_image(path: Path) -> str:
    image = Image.open(path)
    text  = pytesseract.image_to_string(image)
    return text