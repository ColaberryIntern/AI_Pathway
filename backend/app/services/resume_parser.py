"""Resume parsing service — extracts profile fields from PDF/DOCX.

Uses PyPDF2 for PDF text extraction and python-docx for DOCX.
Sends extracted text to the configured LLM provider for structured
field extraction. No agent framework dependency.
"""
import io
import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def _extract_text_pdf(file_bytes: bytes) -> str:
    """Extract text from a PDF file."""
    from PyPDF2 import PdfReader

    reader = PdfReader(io.BytesIO(file_bytes))
    parts = []
    for page in reader.pages:
        text = page.extract_text()
        if text:
            parts.append(text)
    return "\n".join(parts)


def _extract_text_docx(file_bytes: bytes) -> str:
    """Extract text from a DOCX file."""
    from docx import Document

    doc = Document(io.BytesIO(file_bytes))
    parts = []
    for para in doc.paragraphs:
        if para.text.strip():
            parts.append(para.text)
    return "\n".join(parts)


def extract_text(file_bytes: bytes, filename: str) -> str:
    """Extract plain text from a resume file.

    Supports .pdf and .docx formats.
    """
    ext = Path(filename).suffix.lower()
    if ext == ".pdf":
        return _extract_text_pdf(file_bytes)
    elif ext in (".docx", ".doc"):
        return _extract_text_docx(file_bytes)
    else:
        raise ValueError(f"Unsupported file format: {ext}. Please upload a PDF or DOCX file.")


async def parse_resume(file_bytes: bytes, filename: str) -> dict:
    """Parse a resume and extract profile fields using LLM.

    Returns:
        {
            "name": str | None,
            "current_role": str | None,
            "target_role": str | None,
            "industry": str | None,
            "experience_years": int | None,
            "ai_exposure_level": str | None,  # None/Basic/Intermediate/Advanced
        }
    """
    text = extract_text(file_bytes, filename)
    if not text.strip():
        raise ValueError("Could not extract any text from the uploaded file.")

    # Truncate to avoid token limits (resumes are typically short)
    text = text[:8000]

    from app.services.llm import get_llm_provider

    llm = get_llm_provider()

    system_prompt = (
        "You are a resume parser. Extract structured profile information "
        "from the resume text provided. Return ONLY a JSON object with "
        "the specified fields. If a field cannot be determined from the "
        "resume, use null for that field."
    )

    prompt = f"""Extract the following fields from this resume:

1. "name" — The person's full name (string or null)
2. "current_role" — Their most recent job title (string or null)
3. "target_role" — If the resume mentions a career objective or target role, extract it (string or null). If not explicitly stated, infer from career trajectory if possible.
4. "industry" — The primary industry they work in (string or null)
5. "experience_years" — Total years of professional experience as an integer (int or null). Calculate from work history dates if not explicit.
6. "ai_exposure_level" — Their level of AI/ML experience. Must be one of: "None", "Basic", "Intermediate", "Advanced" (string or null).
   - "None": No mention of AI/ML
   - "Basic": Uses AI tools (ChatGPT, Copilot) or mentions AI awareness
   - "Intermediate": Works with AI/ML models, data science, or AI product management
   - "Advanced": Builds/deploys AI systems, ML engineering, AI research

Return ONLY a JSON object with these 6 keys. No additional text.

RESUME TEXT:
{text}"""

    response = await llm.generate(
        prompt=prompt,
        system_prompt=system_prompt,
        temperature=0.1,
        max_tokens=1024,
        json_mode=True,
    )

    try:
        result = json.loads(response.content)
    except json.JSONDecodeError:
        logger.error("LLM returned non-JSON response: %s", response.content[:200])
        raise ValueError("Failed to parse resume. Please try again or fill in the fields manually.")

    # Normalize and validate fields
    return {
        "name": result.get("name") or None,
        "current_role": result.get("current_role") or None,
        "target_role": result.get("target_role") or None,
        "industry": result.get("industry") or None,
        "experience_years": _parse_int(result.get("experience_years")),
        "ai_exposure_level": _validate_ai_level(result.get("ai_exposure_level")),
    }


def _parse_int(value) -> int | None:
    """Safely parse an integer value."""
    if value is None:
        return None
    try:
        return int(value)
    except (ValueError, TypeError):
        return None


def _validate_ai_level(value) -> str | None:
    """Validate AI exposure level."""
    valid = {"None", "Basic", "Intermediate", "Advanced"}
    if value in valid:
        return value
    return None
