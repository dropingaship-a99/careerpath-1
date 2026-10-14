"""Career matching. OWNER: Member 3 (Quiz + scoring).
Career Match = 40% interests + 30% skills + 20% subjects + 10% work values."""

from data.careers import CAREERS, RESOURCES
from data.subjects import SUBJECTS
from data.questions import TYPES, NAMES, SKILLS, VALUES

WEIGHTS = {"interests": 0.4, "skills": 0.3, "subjects": 0.2, "values": 0.1}


def overlap(chosen, wanted):
    """Share of the career's wanted items the student picked (0 to 1).
    If the student picked nothing, stay neutral (0.5) instead of punishing."""
    if not chosen:
        return 0.5
    return len(set(chosen) & set(wanted)) / len(wanted)


def interest_totals(interests):
    """interests = {"R": [2,1,0], ...} -> {"R": 3, ...}. Raises ValueError."""
    if not isinstance(interests, dict):
        raise ValueError("'interests' must be an object like {\"R\": [2,1,0], ...}")
    totals = {}
    for t in TYPES:
        vals = interests.get(t)
        if not isinstance(vals, list) or len(vals) != 3 or any(v not in (0, 1, 2) for v in vals):
            raise ValueError(f"Please answer all 3 questions for type {t} (each answer must be 0, 1 or 2).")
        totals[t] = sum(vals)
    return totals


def format_career(c, picks=None):
    """Career as the website needs it (names instead of codes, resolved links)."""
    skills = [SKILLS[s] for s in c["skills"]]
    chosen = set((picks or {}).get("skills", []))
    return {
        "id": c["id"], "title": c["title"], "category": c["category"],
        "description": c["description"],
        "interest_names": [NAMES[t] for t in c["interests"]],
        "interest_codes": c["interests"],
        "skills": skills, "skill_keys": c["skills"],
        "subjects": [SUBJECTS[s][0] for s in c["subject_codes"]],
        "subject_codes": c["subject_codes"],
        "subject_combo": " + ".join(SUBJECTS[s][0] for s in c["subject_codes"]),
        "work_values": [VALUES[v] for v in c["work_values"]], "value_keys": c["work_values"],
        "advantages": c["advantages"], "challenges": c["challenges"],
        "next_steps": c["next_steps"],
        "skills_to_improve": [SKILLS[s] for s in c["skills"] if s not in chosen] or skills,
        "resources": [{"label": RESOURCES[k][0], "url": RESOURCES[k][1]} for k in c["resources"]],
    }


def recommend(interests, picks, top=5):
    totals = interest_totals(interests)
    ranked = []
    for c in CAREERS:
        first, second = c["interests"]
        parts = {
            "interests": (2 * totals[first] + totals[second]) / 18,
            "skills": overlap(picks["skills"], c["skills"]),
            "subjects": overlap(picks["subjects"], c["subject_codes"]),
            "values": overlap(picks["values"], c["work_values"]),
        }
        score = sum(WEIGHTS[k] * parts[k] for k in WEIGHTS)
        ranked.append((score, parts, c))
    ranked.sort(key=lambda r: -r[0])

    results = []
    for score, parts, c in ranked[:top]:
        out = format_career(c, picks)
        out["match"] = round(score * 100)
        out["breakdown"] = {k: round(v * 100) for k, v in parts.items()}
        out["why"] = why_text(c, totals, picks)
        results.append(out)
    top_types = sorted(TYPES, key=lambda t: (-totals[t], TYPES.index(t)))[:3]
    return {"profile": [{"type": t, "name": NAMES[t], "score": totals[t]} for t in top_types],
            "careers": results}


def why_text(c, totals, picks):
    bits = []
    t = c["interests"][0]
    if totals[t] >= 3:
        bits.append(f"you scored well on the {NAMES[t]} interest")
    sk = [SKILLS[s] for s in c["skills"] if s in picks["skills"]]
    if sk:
        bits.append("you already have " + ", ".join(sk).lower())
    sb = [SUBJECTS[s][0] for s in c["subject_codes"] if s in picks["subjects"]]
    if sb:
        bits.append("you like " + ", ".join(sb))
    vl = [VALUES[v] for v in c["work_values"] if v in picks["values"]]
    if vl:
        bits.append("it fits what you value: " + ", ".join(vl).lower())
    if not bits:
        return "This is a broad idea worth a quick look. Your answers match it only a little."
    return "This may suit you because " + "; ".join(bits) + "."
