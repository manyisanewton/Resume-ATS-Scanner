import re
from pathlib import Path

COMMON_SKILLS = {
    "python",
    "flask",
    "django",
    "postgresql",
    "mysql",
    "sql",
    "react",
    "javascript",
    "typescript",
    "aws",
    "docker",
    "kubernetes",
    "git",
}


def parse_resume_file(file_path: str) -> str:
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"resume file not found: {file_path}")

    ext = path.suffix.lower()
    if ext == ".txt":
        return path.read_text(encoding="utf-8", errors="ignore")
    if ext == ".pdf":
        return _parse_pdf(path)
    if ext == ".docx":
        return _parse_docx(path)

    return path.read_text(encoding="utf-8", errors="ignore")


def extract_profile_from_text(text: str) -> dict:
    lowered = (text or "").lower()
    found_skills = sorted([skill for skill in COMMON_SKILLS if skill in lowered])

    years = None
    years_match = re.search(r"(\d{1,2})\s*\+?\s*years?", lowered)
    if years_match:
        years = int(years_match.group(1))

    education = None
    for level in ["phd", "master", "bachelor"]:
        if level in lowered:
            education = level
            break

    return {
        "skills": found_skills,
        "years_experience": years,
        "education": education,
    }


def _parse_pdf(path: Path) -> str:
    try:
        from pypdf import PdfReader
    except ImportError as exc:
        raise RuntimeError("pypdf is required to parse PDF resumes") from exc

    reader = PdfReader(str(path))
    parts = []
    for page in reader.pages:
        parts.append(page.extract_text() or "")
    return "\n".join(parts).strip()


def _parse_docx(path: Path) -> str:
    try:
        import docx
    except ImportError as exc:
        raise RuntimeError("python-docx is required to parse DOCX resumes") from exc

    document = docx.Document(str(path))
    return "\n".join(paragraph.text for paragraph in document.paragraphs).strip()
