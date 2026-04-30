from __future__ import annotations

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from app.schemas import (
    ChatMessage,
    ChatResponse,
    CoverLetterRequest,
    CoverLetterResponse,
    InterviewRequest,
    InterviewResponse,
    RecommendationRequest,
    ResumeAnalysis,
)
from app.services.analyzer import analyze_resume
from app.services.cover_letter import generate_cover_letter
from app.services.interview import generate_interview_questions
from app.services.llm import answer_chat
from app.services.recommender import recommend_jobs
from app.services.resume_parser import extract_text_from_upload, parse_resume_text


app = FastAPI(title="AI Career Assistant API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/resume/analyze", response_model=ResumeAnalysis)
async def analyze_resume_upload(file: UploadFile = File(...)) -> ResumeAnalysis:
    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Upload a non-empty resume file.")

    try:
        text = await extract_text_from_upload(file.filename or "resume.txt", content)
    except RuntimeError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    parsed = parse_resume_text(text)
    if len(parsed.text) < 40:
        raise HTTPException(status_code=422, detail="The resume text is too short to analyze.")
    return analyze_resume(parsed)


@app.post("/api/resume/analyze-text", response_model=ResumeAnalysis)
def analyze_resume_text(payload: dict[str, str]) -> ResumeAnalysis:
    text = payload.get("text", "")
    if len(text.strip()) < 40:
        raise HTTPException(status_code=422, detail="Paste at least 40 characters of resume text.")
    return analyze_resume(parse_resume_text(text))


@app.post("/api/jobs/recommend")
def recommend(payload: RecommendationRequest):
    return {"roles": recommend_jobs(payload.skills, limit=8)}


@app.post("/api/chat", response_model=ChatResponse)
async def chat(payload: ChatMessage) -> ChatResponse:
    if not payload.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty.")
    return await answer_chat(payload)


@app.post("/api/interview", response_model=InterviewResponse)
def interview(payload: InterviewRequest) -> InterviewResponse:
    return InterviewResponse(
        role=payload.role,
        questions=generate_interview_questions(payload.role, include_answers=payload.include_answers),
    )


@app.post("/api/cover-letter", response_model=CoverLetterResponse)
def cover_letter(payload: CoverLetterRequest) -> CoverLetterResponse:
    return CoverLetterResponse(
        cover_letter=generate_cover_letter(payload.role, payload.company, payload.profile)
    )
