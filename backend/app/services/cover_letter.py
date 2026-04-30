from __future__ import annotations

from app.schemas import Profile


def generate_cover_letter(role: str, company: str, profile: Profile) -> str:
    skills = ", ".join(profile.skills[:8]) if profile.skills else "relevant technical and analytical skills"
    education = ", ".join(profile.education[:2]) if profile.education else "my academic and project background"
    years = f"{profile.experience_years:g} years of experience" if profile.experience_years else "hands-on project experience"

    return (
        f"Dear {company},\n\n"
        f"I am excited to apply for the {role} position. My background combines {education}, "
        f"{years}, and practical experience with {skills}. I enjoy turning ambiguous problems into clear, useful outcomes, "
        f"and I would bring that same structured approach to your team.\n\n"
        f"In my recent work, I have focused on building projects that show both technical execution and business thinking. "
        f"I can learn quickly, communicate tradeoffs clearly, and keep improving a solution until it is useful for real users.\n\n"
        f"I would welcome the opportunity to discuss how my skills can support your goals for this role.\n\n"
        f"Sincerely,\n"
        f"Your Name"
    )
