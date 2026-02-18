import json
import re
from dataclasses import dataclass

DEFAULT_WEIGHTS = {
    "skills": 0.45,
    "experience": 0.25,
    "education": 0.10,
    "keywords": 0.20,
}

STOP_WORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "for",
    "from",
    "in",
    "is",
    "it",
    "of",
    "on",
    "or",
    "that",
    "the",
    "to",
    "with",
}


@dataclass
class ScoreResult:
    total_score: float
    breakdown: dict


def _normalize_weights(weights: dict | None) -> dict:
    base = dict(DEFAULT_WEIGHTS)
    if weights:
        for key in base:
            if key in weights and isinstance(weights[key], (int, float)):
                base[key] = float(weights[key])

    total = sum(base.values())
    if total <= 0:
        return dict(DEFAULT_WEIGHTS)

    return {k: v / total for k, v in base.items()}


def _tokenize(text: str) -> list[str]:
    tokens = re.findall(r"[a-zA-Z0-9+#.]+", (text or "").lower())
    return [t for t in tokens if t not in STOP_WORDS and len(t) > 1]


def _extract_years(text: str) -> int | None:
    match = re.search(r"(\d{1,2})\s*\+?\s*years?", (text or "").lower())
    if not match:
        return None
    return int(match.group(1))


def _skills_from_profile(profile_json: dict | None) -> set[str]:
    if not isinstance(profile_json, dict):
        return set()

    skills = profile_json.get("skills")
    if isinstance(skills, list):
        return {str(skill).strip().lower() for skill in skills if str(skill).strip()}
    return set()


def _build_candidate_text(candidate: dict) -> str:
    parts = [
        candidate.get("full_name") or "",
        candidate.get("resume_filename") or "",
        candidate.get("extracted_text") or "",
    ]

    profile_json = candidate.get("profile_json")
    if isinstance(profile_json, dict):
        parts.extend(profile_json.get("skills", []))
        years = profile_json.get("years_experience")
        if years is not None:
            parts.append(f"{years} years")
        education = profile_json.get("education")
        if education is not None:
            parts.append(str(education))

    return " ".join(str(part) for part in parts)


def _extract_jd_skill_terms(jd_text: str, limit: int = 20) -> list[str]:
    terms = []
    seen = set()
    for token in _tokenize(jd_text):
        if token in seen:
            continue
        seen.add(token)
        terms.append(token)
        if len(terms) == limit:
            break
    return terms


def _load_json(raw: str | None) -> dict | None:
    if not raw:
        return None
    try:
        loaded = json.loads(raw)
    except json.JSONDecodeError:
        return None
    return loaded if isinstance(loaded, dict) else None


def score_candidate_against_jd(candidate: dict, jd: dict, weights: dict | None = None) -> ScoreResult:
    normalized_weights = _normalize_weights(weights)

    jd_text = jd.get("text") or ""
    candidate_text = _build_candidate_text(candidate)
    candidate_terms = set(_tokenize(candidate_text))
    jd_terms = set(_tokenize(jd_text))
    jd_skill_terms = _extract_jd_skill_terms(jd_text)

    matched_skills = [skill for skill in jd_skill_terms if skill in candidate_terms]
    missing_skills = [skill for skill in jd_skill_terms if skill not in candidate_terms]
    skill_score = (len(matched_skills) / len(jd_skill_terms) * 100.0) if jd_skill_terms else 0.0

    profile_json = candidate.get("profile_json")
    if isinstance(profile_json, str):
        profile_json = _load_json(profile_json)

    profile_skills = _skills_from_profile(profile_json)
    if profile_skills and jd_skill_terms:
        profile_matches = len([s for s in jd_skill_terms if s in profile_skills])
        profile_skill_score = profile_matches / len(jd_skill_terms) * 100.0
        skill_score = max(skill_score, profile_skill_score)

    required_years = _extract_years(jd_text)
    candidate_years = None
    if isinstance(profile_json, dict) and isinstance(profile_json.get("years_experience"), (int, float)):
        candidate_years = int(profile_json["years_experience"])
    if candidate_years is None:
        candidate_years = _extract_years(candidate_text)

    if required_years is None:
        experience_score = 100.0
    elif candidate_years is None:
        experience_score = 0.0
    else:
        experience_score = min(candidate_years / required_years, 1.0) * 100.0

    jd_lower = jd_text.lower()
    candidate_lower = candidate_text.lower()
    required_education = None
    for level in ["phd", "master", "bachelor"]:
        if level in jd_lower:
            required_education = level
            break

    if required_education is None:
        education_score = 100.0
    else:
        education_score = 100.0 if required_education in candidate_lower else 0.0

    union = jd_terms.union(candidate_terms)
    keyword_score = (len(jd_terms.intersection(candidate_terms)) / len(union) * 100.0) if union else 0.0

    total_score = (
        normalized_weights["skills"] * skill_score
        + normalized_weights["experience"] * experience_score
        + normalized_weights["education"] * education_score
        + normalized_weights["keywords"] * keyword_score
    )

    breakdown = {
        "weights": normalized_weights,
        "skills": {
            "score": round(skill_score, 2),
            "matched": matched_skills,
            "missing": missing_skills,
        },
        "experience": {
            "score": round(experience_score, 2),
            "required_years": required_years,
            "candidate_years": candidate_years,
        },
        "education": {
            "score": round(education_score, 2),
            "required": required_education,
        },
        "keywords": {
            "score": round(keyword_score, 2),
        },
    }

    return ScoreResult(total_score=round(total_score, 2), breakdown=breakdown)
