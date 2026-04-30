from __future__ import annotations

import os

import httpx

from app.schemas import ChatMessage, ChatResponse, ResumeAnalysis
from app.services.interview import generate_interview_questions
from app.services.recommender import recommend_jobs


HF_API_TOKEN = os.getenv("HF_API_TOKEN")
HF_MODEL = os.getenv("HF_MODEL", "mistralai/Mistral-7B-Instruct-v0.3")


async def answer_chat(payload: ChatMessage) -> ChatResponse:
    if HF_API_TOKEN:
        response = await _answer_with_hugging_face(payload)
        if response:
            return ChatResponse(answer=response, source="hugging-face")
    return ChatResponse(answer=_answer_locally(payload), source="local")


async def _answer_with_hugging_face(payload: ChatMessage) -> str | None:
    prompt = _build_prompt(payload)
    headers = {"Authorization": f"Bearer {HF_API_TOKEN}"}
    body = {"inputs": prompt, "parameters": {"max_new_tokens": 420, "temperature": 0.4, "return_full_text": False}}

    try:
        async with httpx.AsyncClient(timeout=25) as client:
            response = await client.post(f"https://api-inference.huggingface.co/models/{HF_MODEL}", headers=headers, json=body)
            response.raise_for_status()
            data = response.json()
    except Exception:
        return None

    if isinstance(data, list) and data and isinstance(data[0], dict):
        return data[0].get("generated_text")
    if isinstance(data, dict):
        return data.get("generated_text") or data.get("summary_text")
    return None


def _answer_locally(payload: ChatMessage) -> str:
    message = payload.message.lower()
    analysis = payload.analysis
    profile = payload.profile or (analysis.profile if analysis else None)

    if "job" in message or "role" in message or "fit" in message:
        skills = profile.skills if profile else []
        matches = analysis.recommended_roles if analysis else recommend_jobs(skills)
        lines = [f"{match.role}: {match.match_percentage}% match because of {', '.join(match.matched_skills) or 'transferable skills'}." for match in matches[:5]]
        return "Best-fit roles:\n" + "\n".join(f"- {line}" for line in lines)

    if "improve" in message or "resume" in message:
        suggestions = analysis.suggestions if analysis else [
            "Add a keyword-rich skills section.",
            "Quantify project impact with metrics.",
            "Tailor the summary to one target role.",
        ]
        return "Resume improvements:\n" + "\n".join(f"- {item}" for item in suggestions)

    if "interview" in message or "question" in message:
        role = analysis.recommended_roles[0].role if analysis and analysis.recommended_roles else "your target role"
        questions = generate_interview_questions(role, include_answers=False)[:5]
        return "Interview practice questions:\n" + "\n".join(f"- {item['question']}" for item in questions)

    if "skill" in message or "missing" in message or "gap" in message:
        missing = analysis.missing_skills if analysis else []
        if not missing:
            return "I need a resume analysis first to identify precise skill gaps."
        return "Skill gaps to work on:\n" + "\n".join(f"- {skill}" for skill in missing)

    if "roadmap" in message or "learn" in message:
        if analysis and analysis.recommended_roles:
            match = analysis.recommended_roles[0]
            return f"Roadmap for {match.role}:\n" + "\n".join(f"{index}. {step}" for index, step in enumerate(match.roadmap, start=1))
        return "Pick a target role first, then I can create a focused learning roadmap."

    return (
        "I can help with job fit, resume improvements, missing skills, interview questions, and roadmaps. "
        "Upload or paste a resume first for the most personalized answer."
    )


def _build_prompt(payload: ChatMessage) -> str:
    analysis_block = _analysis_summary(payload.analysis)
    return (
        "You are an AI career assistant. Give concise, practical, personalized career guidance.\n\n"
        f"Resume context:\n{analysis_block}\n\n"
        f"User question: {payload.message}\n\n"
        "Answer with bullet points when useful."
    )


def _analysis_summary(analysis: ResumeAnalysis | None) -> str:
    if not analysis:
        return "No resume analysis is available yet."
    roles = ", ".join(f"{match.role} ({match.match_percentage}%)" for match in analysis.recommended_roles[:3])
    return (
        f"Score: {analysis.score}/100\n"
        f"Skills: {', '.join(analysis.profile.skills)}\n"
        f"Experience years: {analysis.profile.experience_years:g}\n"
        f"Education: {', '.join(analysis.profile.education) or 'not detected'}\n"
        f"Missing skills: {', '.join(analysis.missing_skills)}\n"
        f"Recommended roles: {roles}"
    )
