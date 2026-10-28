from dataclasses import dataclass


@dataclass(frozen=True)
class SkillMatch:
    skill: str
    found_in_cv: bool
    evidence: str | None  # Exact quote from the CV


@dataclass(frozen=True)
class CVEvaluation:
    score: int  # 0 to 100
    summary: str
    matched_skills: list[SkillMatch]
    missing_skills: list[str]
    experience_gap: str
