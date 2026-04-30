from __future__ import annotations

from app.schemas import ResumeAnalysis
from app.services.recommender import recommend_jobs, top_missing_skills
from app.services.resume_parser import ParsedResume


def analyze_resume(parsed: ParsedResume) -> ResumeAnalysis:
    matches = recommend_jobs(parsed.skills)
    missing_skills = top_missing_skills(matches)
    score, explanation = score_resume(parsed, matches)

    return ResumeAnalysis(
        profile={
            "skills": parsed.skills,
            "experience_years": parsed.experience_years,
            "education": parsed.education,
            "resume_text": parsed.text,
        },
        score=score,
        score_explanation=explanation,
        missing_skills=missing_skills,
        suggestions=build_suggestions(parsed, missing_skills, matches),
        recommended_roles=matches,
    )


def score_resume(parsed: ParsedResume, matches) -> tuple[int, list[str]]:
    skill_score = min(45, len(parsed.skills) * 5)
    experience_score = min(20, round(parsed.experience_years * 5))
    education_score = 15 if parsed.education else 4
    keyword_score = min(20, round((matches[0].match_percentage if matches else 0) * 0.2))
    score = max(0, min(100, skill_score + experience_score + education_score + keyword_score))

    explanation = [
        f"Skill coverage contributes {skill_score}/45 based on {len(parsed.skills)} detected skills.",
        f"Experience contributes {experience_score}/20 from {parsed.experience_years:g} detected years.",
        f"Education contributes {education_score}/15 based on detected degree or certification signals.",
        f"Role alignment contributes {keyword_score}/20 from the strongest job match.",
    ]
    return score, explanation


def build_suggestions(parsed: ParsedResume, missing_skills: list[str], matches) -> list[str]:
    suggestions: list[str] = []
    if len(parsed.skills) < 6:
        suggestions.append("Add a dedicated skills section with tools, languages, and domain skills written as exact keywords.")
    if parsed.experience_years == 0:
        suggestions.append("Mention internship, project, or work experience with clear timelines so years of experience can be inferred.")
    if not parsed.education:
        suggestions.append("Add education, degree, certification, or relevant coursework details.")
    if missing_skills:
        suggestions.append(f"Prioritize these high-impact missing skills: {', '.join(missing_skills[:4])}.")
    if matches:
        suggestions.append(f"Tailor the resume headline and project bullets toward {matches[0].role} roles.")
    suggestions.append("Rewrite project bullets with action, tool, metric, and outcome, for example: Built X using Y, improving Z by N%.")
    return suggestions[:6]
