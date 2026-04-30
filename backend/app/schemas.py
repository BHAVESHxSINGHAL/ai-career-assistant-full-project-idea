from __future__ import annotations

from pydantic import BaseModel, Field


class Profile(BaseModel):
    skills: list[str] = Field(default_factory=list)
    experience_years: float = 0
    education: list[str] = Field(default_factory=list)
    resume_text: str = ""


class JobMatch(BaseModel):
    role: str
    category: str
    description: str
    match_percentage: int
    matched_skills: list[str]
    missing_skills: list[str]
    roadmap: list[str]


class ResumeAnalysis(BaseModel):
    profile: Profile
    score: int
    score_explanation: list[str]
    missing_skills: list[str]
    suggestions: list[str]
    recommended_roles: list[JobMatch]


class ChatMessage(BaseModel):
    message: str
    profile: Profile | None = None
    analysis: ResumeAnalysis | None = None


class ChatResponse(BaseModel):
    answer: str
    source: str = "local"


class RecommendationRequest(BaseModel):
    skills: list[str] = Field(default_factory=list)


class InterviewRequest(BaseModel):
    role: str
    include_answers: bool = True


class InterviewQuestion(BaseModel):
    question: str
    answer: str | None = None
    kind: str


class InterviewResponse(BaseModel):
    role: str
    questions: list[InterviewQuestion]


class CoverLetterRequest(BaseModel):
    role: str
    company: str = "Hiring Team"
    profile: Profile


class CoverLetterResponse(BaseModel):
    cover_letter: str
