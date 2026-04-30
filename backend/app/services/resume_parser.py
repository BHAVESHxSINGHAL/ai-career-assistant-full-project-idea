from __future__ import annotations

import io
import re
from dataclasses import dataclass


SKILL_ALIASES: dict[str, list[str]] = {
    "python": ["python", "py"],
    "sql": ["sql", "mysql", "postgresql", "postgres", "sqlite"],
    "excel": ["excel", "spreadsheets", "pivot table", "pivot tables"],
    "power bi": ["power bi", "powerbi"],
    "tableau": ["tableau"],
    "statistics": ["statistics", "statistical analysis", "hypothesis testing"],
    "data visualization": ["data visualization", "visualisation", "dashboard", "dashboards"],
    "pandas": ["pandas"],
    "numpy": ["numpy"],
    "machine learning": ["machine learning", "ml"],
    "scikit-learn": ["scikit-learn", "sklearn"],
    "model evaluation": ["model evaluation", "precision", "recall", "f1 score", "roc"],
    "deep learning": ["deep learning", "neural network", "neural networks"],
    "pytorch": ["pytorch", "torch"],
    "tensorflow": ["tensorflow"],
    "nlp": ["nlp", "natural language processing"],
    "llm": ["llm", "large language model", "language models"],
    "prompt engineering": ["prompt engineering", "prompt design"],
    "rag": ["rag", "retrieval augmented generation", "retrieval-augmented generation"],
    "vector databases": ["vector database", "vector databases", "faiss", "pinecone", "chroma"],
    "fastapi": ["fastapi"],
    "mongodb": ["mongodb", "mongo"],
    "rest api": ["rest api", "restful api", "api development"],
    "api integration": ["api integration", "apis", "api"],
    "authentication": ["authentication", "auth", "jwt", "oauth"],
    "testing": ["testing", "unit testing", "pytest", "test automation"],
    "javascript": ["javascript", "js"],
    "typescript": ["typescript", "ts"],
    "react": ["react", "reactjs", "react.js"],
    "html": ["html"],
    "css": ["css"],
    "responsive design": ["responsive design", "mobile first", "mobile-first"],
    "git": ["git", "github", "version control"],
    "communication": ["communication", "presentation", "presentations"],
    "business analysis": ["business analysis", "business analyst"],
    "requirements gathering": ["requirements gathering", "requirement gathering", "user stories"],
    "documentation": ["documentation", "technical writing"],
    "jira": ["jira"],
    "stakeholder management": ["stakeholder management", "stakeholders"],
    "process mapping": ["process mapping", "process improvement"],
    "analytics": ["analytics", "data analysis"],
    "a/b testing": ["a/b testing", "ab testing", "experimentation"],
    "selenium": ["selenium"],
    "playwright": ["playwright"],
    "api testing": ["api testing", "postman"],
    "bug reporting": ["bug reporting", "bug reports"],
    "ci/cd": ["ci/cd", "github actions", "continuous integration"],
    "docker": ["docker", "containerization"],
}


EDUCATION_PATTERNS = [
    r"\bB\.?Tech\b|\bBachelor(?:'s)?\b|\bBSc\b|\bB\.?Sc\b|\bBCA\b|\bBBA\b",
    r"\bM\.?Tech\b|\bMaster(?:'s)?\b|\bMSc\b|\bM\.?Sc\b|\bMCA\b|\bMBA\b",
    r"\bPh\.?D\b|\bDoctorate\b",
    r"\bDiploma\b|\bCertificate\b|\bCertification\b",
]


@dataclass(frozen=True)
class ParsedResume:
    text: str
    skills: list[str]
    experience_years: float
    education: list[str]


async def extract_text_from_upload(filename: str, content: bytes) -> str:
    suffix = filename.lower().rsplit(".", 1)[-1] if "." in filename else ""
    if suffix == "pdf":
        return _extract_pdf_text(content)
    return content.decode("utf-8", errors="ignore")


def parse_resume_text(text: str) -> ParsedResume:
    normalized = _normalize_text(text)
    return ParsedResume(
        text=text.strip(),
        skills=extract_skills(normalized),
        experience_years=extract_experience_years(normalized),
        education=extract_education(text),
    )


def extract_skills(normalized_text: str) -> list[str]:
    found: set[str] = set()
    for canonical, aliases in SKILL_ALIASES.items():
        if any(_contains_skill(normalized_text, alias) for alias in aliases):
            found.add(canonical)
    return sorted(found)


def extract_experience_years(normalized_text: str) -> float:
    patterns = [
        r"(\d+(?:\.\d+)?)\+?\s*(?:years?|yrs?)\s+(?:of\s+)?experience",
        r"experience\s*(?:of|:)?\s*(\d+(?:\.\d+)?)\+?\s*(?:years?|yrs?)",
    ]
    matches: list[float] = []
    for pattern in patterns:
        for match in re.findall(pattern, normalized_text, flags=re.IGNORECASE):
            try:
                matches.append(float(match))
            except ValueError:
                continue
    return max(matches) if matches else 0


def extract_education(text: str) -> list[str]:
    education: set[str] = set()
    for pattern in EDUCATION_PATTERNS:
        for match in re.findall(pattern, text, flags=re.IGNORECASE):
            education.add(match.strip())
    return sorted(education)


def _extract_pdf_text(content: bytes) -> str:
    try:
        from pypdf import PdfReader
    except ImportError as exc:
        raise RuntimeError(
            "PDF parsing requires the optional 'pypdf' package. Install backend requirements or upload a .txt resume."
        ) from exc

    reader = PdfReader(io.BytesIO(content))
    pages = [page.extract_text() or "" for page in reader.pages]
    return "\n".join(pages)


def _normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower())


def _contains_skill(normalized_text: str, alias: str) -> bool:
    escaped = re.escape(alias.lower())
    return re.search(rf"(?<![a-z0-9+#]){escaped}(?![a-z0-9+#])", normalized_text) is not None
