import json

from docai.factories import get_llm
from docai.features.cv.prompts import get_cv_prompts
from docai.features.cv.schema import CVEvaluation, SkillMatch


def evaluate_cv(cv_text: str, jd_text: str, language: str = "en") -> CVEvaluation:
    """Evaluate a CV against a Job Description using the LLM."""
    prompts = get_cv_prompts(language)
    prompt = prompts.USER_TEMPLATE.format(cv=cv_text, jd=jd_text)

    # Call the LLM
    response = get_llm().complete(prompt, system=prompts.SYSTEM)

    # Clean the response in case the LLM wrapped it in markdown blocks
    clean_json = (
        response.strip()
        .removeprefix("```json")
        .removeprefix("```")
        .removesuffix("```")
        .strip()
    )

    try:
        data = json.loads(clean_json)
    except json.JSONDecodeError as e:
        raise ValueError(
            f"LLM failed to return valid JSON: {e}\nRaw response: {response}"
        )

    # Map the JSON back to our dataclasses
    matched = [
        SkillMatch(
            skill=m.get("skill", ""),
            found_in_cv=m.get("found_in_cv", False),
            evidence=m.get("evidence"),
        )
        for m in data.get("matched_skills", [])
    ]

    return CVEvaluation(
        score=data.get("score", 0),
        summary=data.get("summary", ""),
        matched_skills=matched,
        missing_skills=data.get("missing_skills", []),
        experience_gap=data.get("experience_gap", ""),
    )
