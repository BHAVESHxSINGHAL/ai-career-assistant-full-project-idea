from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

from app.schemas import JobMatch


DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "jobs.json"


@lru_cache
def load_jobs() -> list[dict]:
    return json.loads(DATA_PATH.read_text(encoding="utf-8"))


def recommend_jobs(skills: list[str], limit: int = 5) -> list[JobMatch]:
    normalized_skills = {skill.strip().lower() for skill in skills if skill.strip()}
    matches: list[JobMatch] = []

    for job in load_jobs():
        required = {skill.lower() for skill in job["required_skills"]}
        nice = {skill.lower() for skill in job.get("nice_to_have", [])}
        matched_required = sorted(required & normalized_skills)
        matched_nice = sorted(nice & normalized_skills)
        weighted_total = (len(required) * 2) + len(nice)
        weighted_match = (len(matched_required) * 2) + len(matched_nice)
        percentage = round((weighted_match / weighted_total) * 100) if weighted_total else 0

        matches.append(
            JobMatch(
                role=job["role"],
                category=job["category"],
                description=job["description"],
                match_percentage=min(100, percentage),
                matched_skills=sorted(set(matched_required + matched_nice)),
                missing_skills=sorted(required - normalized_skills),
                roadmap=job["roadmap"],
            )
        )

    return sorted(matches, key=lambda item: item.match_percentage, reverse=True)[:limit]


def top_missing_skills(matches: list[JobMatch], limit: int = 6) -> list[str]:
    counts: dict[str, int] = {}
    for match in matches[:3]:
        for skill in match.missing_skills:
            counts[skill] = counts.get(skill, 0) + 1
    return [skill for skill, _ in sorted(counts.items(), key=lambda item: (-item[1], item[0]))[:limit]]
