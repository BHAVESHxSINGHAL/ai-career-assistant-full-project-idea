from __future__ import annotations


ROLE_TOPICS: dict[str, list[str]] = {
    "data analyst": ["SQL joins", "dashboard design", "statistics", "business metrics"],
    "business analyst": ["requirements gathering", "stakeholder communication", "process mapping", "prioritization"],
    "machine learning intern": ["model evaluation", "feature engineering", "overfitting", "scikit-learn"],
    "ai engineer": ["prompt engineering", "RAG", "API design", "LLM evaluation"],
    "frontend developer": ["React state", "responsive CSS", "API loading states", "accessibility"],
    "backend developer": ["FastAPI", "database modeling", "authentication", "testing"],
    "product analyst": ["funnels", "cohorts", "A/B testing", "retention"],
    "qa automation engineer": ["test planning", "API testing", "browser automation", "bug reports"],
}


def generate_interview_questions(role: str, include_answers: bool = True) -> list[dict[str, str | None]]:
    topics = ROLE_TOPICS.get(role.lower(), ["core skills", "projects", "problem solving", "communication"])
    questions: list[dict[str, str | None]] = []

    for topic in topics:
        question = f"How would you explain your experience with {topic} for a {role} role?"
        questions.append(
            {
                "kind": "technical",
                "question": question,
                "answer": _answer_for(topic, role) if include_answers else None,
            }
        )

    hr_questions = [
        "Tell me about a project you are proud of and the impact it created.",
        "Describe a time you learned a new skill quickly.",
        "Why are you interested in this role?",
    ]
    for question in hr_questions:
        questions.append(
            {
                "kind": "hr",
                "question": question,
                "answer": _hr_answer(question, role) if include_answers else None,
            }
        )

    return questions


def _answer_for(topic: str, role: str) -> str:
    return (
        f"Use a project-based answer: name the problem, explain how you used {topic}, "
        f"state the decision you made, and close with a measurable result relevant to {role}."
    )


def _hr_answer(question: str, role: str) -> str:
    if "Why" in question:
        return f"Connect your skills, projects, and learning goals to the daily work of a {role}."
    return "Use the STAR format: situation, task, action, result. Keep the result specific and measurable."
