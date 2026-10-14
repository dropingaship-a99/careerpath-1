"""Unified career catalogue used by the ML engine.

It merges two sources:
  1. The 23 careers shown in the Next.js UI (frontend/lib/career-data.ts, parsed at start-up
     so the ML always sees the same careers the UI can open).
  2. The 18 PathFinder careers (backend/data/careers.py) that carry RIASEC interests, skills,
     school subjects and work values.

Careers that exist in both (same id) keep the UI text and take the PathFinder features.
The remaining UI-only careers get hand-written features below (UI_FEATURES).
"""
import json
import os
import re

from data.careers import CAREERS as PF_CAREERS, RESOURCES
from data.questions import SKILLS, VALUES

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
TS_PATH = os.path.join(ROOT, "frontend", "lib", "career-data.ts")
SNAPSHOT = os.path.join(os.path.dirname(HERE), "data", "ui_careers.json")

# Features for UI careers that PathFinder does not have.
# id: (RIASEC letters strongest first, skills, subject short codes, work values)
UI_FEATURES = {
    "software-engineer":  ("IC", "coding problem maths teamwork", "CS MATH STAT", "technology income independence"),
    "data-scientist":     ("IC", "maths coding research problem", "STAT MATH CS ECO", "technology income"),
    "cloud-architect":    ("IC", "coding problem organising teamwork", "CS ELE MATH", "technology income stability"),
    "research-scientist": ("IR", "research problem maths writing", "PHY CHM BIO MATH", "independence stability technology"),
    "biotechnologist":    ("IR", "research hands problem teamwork", "BIO CHM MATH", "helping technology nature"),
    "astrophysicist":     ("IR", "maths research problem coding", "PHY MATH CS", "independence technology"),
    "psychologist":       ("SI", "empathy research speaking writing", "PSY BIO SOC ENG", "helping stability"),
    "pharmacist":         ("CI", "organising research empathy", "CHM BIO", "helping stability income"),
    "business-analyst":   ("EC", "problem speaking organising teamwork", "BUS ECO STAT MATH", "income technology stability"),
    "marketing-manager":  ("EA", "speaking writing leadership teamwork", "BUS MED ENG PSY", "income creativity"),
    "investment-banker":  ("EC", "maths speaking leadership organising", "ECO BUS MATH", "income"),
    "corporate-lawyer":   ("EC", "speaking writing research organising", "ENG SOC BUS ECO", "income stability"),
    "judge":              ("SC", "research writing organising speaking", "SOC ENG ECO", "stability helping"),
    "legal-advisor":      ("CE", "research writing organising speaking", "SOC ENG BUS", "stability helping income"),
    "criminal-lawyer":    ("ES", "speaking research writing problem", "SOC ENG PSY", "helping independence"),
    "civil-engineer":     ("RE", "maths hands problem organising teamwork", "MATH PHY GEO ENV", "stability income"),
    "pilot":              ("RC", "maths hands problem organising", "PHY MATH GEO", "income technology independence"),
}

# PathFinder category -> the UI's six "areas" (used for the area boost)
CATEGORY_TO_FIELD = {
    "Technology": "technology", "Health": "healthcare", "Design": "other", "Environment": "science",
    "Business": "business", "Sports": "other", "Public Service": "other", "Agriculture": "science",
    "Skilled Trades": "technology", "Arts and Media": "other",
}

# UI id -> PathFinder id when they are the same job under two names.
ALIASES = {"chartered-accountant": "accountant"}


def _str(m):
    s = m.strip()
    if s[:1] in "'\"" and s[-1:] == s[:1]:
        s = s[1:-1]
    return s.replace("\\'", "'").replace('\\"', '"')


def _parse_ts(text):
    """Pull the text fields we need out of the seed({...}) blocks of career-data.ts."""
    out = []
    str_re = r"""('(?:[^'\\]|\\.)*'|"(?:[^"\\]|\\.)*")"""
    for block in re.split(r"\n\s*seed\(\{", text)[1:]:
        block = block.split("\n  }),")[0]
        rec = {}
        for key in ("id", "name", "description", "category", "field", "overview", "future",
                    "salary", "demand", "growth"):
            m = re.search(r"\n\s*" + key + r":\s*" + str_re, block)
            if m:
                rec[key] = _str(m.group(1))
        for key in ("roles", "companies", "benefits", "skills"):
            m = re.search(r"\n\s*" + key + r":\s*\[(.*?)\]", block, re.S)
            rec[key] = [_str(x) for x in re.findall(str_re, m.group(1))] if m else []
        if rec.get("id") and rec.get("name"):
            out.append(rec)
    return out


def load_ui_careers():
    """Parse the TypeScript file; fall back to the bundled snapshot if it is missing."""
    try:
        with open(TS_PATH, encoding="utf-8") as f:
            careers = _parse_ts(f.read())
        if careers:
            try:
                with open(SNAPSHOT, "w", encoding="utf-8") as f:
                    json.dump(careers, f, indent=1, ensure_ascii=False)
            except OSError:
                pass
            return careers
    except OSError:
        pass
    with open(SNAPSHOT, encoding="utf-8") as f:
        return json.load(f)


def _resources(keys):
    return [{"label": RESOURCES[k][0], "url": RESOURCES[k][1]} for k in keys if k in RESOURCES]


def build_catalogue():
    """List of dicts, one per career, all with the same feature fields."""
    pf = {c["id"]: c for c in PF_CAREERS}
    ui = load_ui_careers()
    used_pf = set()
    out = []
    for u in ui:
        pid = u["id"] if u["id"] in pf else ALIASES.get(u["id"])
        if pid in pf:
            p = pf[pid]
            used_pf.add(pid)
            feats = dict(interests=p["interests"], skills=p["skills"],
                         subjects=[s.split("-")[0] for s in p["subject_codes"]], values=p["work_values"])
            extra = dict(next_steps=p["next_steps"], resources=_resources(p["resources"]))
        elif u["id"] in UI_FEATURES:
            i, s, sub, v = UI_FEATURES[u["id"]]
            feats = dict(interests=list(i), skills=s.split(), subjects=sub.split(), values=v.split())
            extra = dict(next_steps=[], resources=[])
        else:  # a career someone added to the UI later: still searchable, no features yet
            feats = dict(interests=[], skills=[], subjects=[], values=[])
            extra = dict(next_steps=[], resources=[])
        out.append(dict(id=u["id"], title=u["name"], source="ui", in_ui=True,
                        category=u.get("category", ""), field=u.get("field", "other"), description=u.get("description", ""),
                        overview=u.get("overview", ""), roles=u.get("roles", []),
                        ui_skills=u.get("skills", []), salary=u.get("salary", ""),
                        growth=u.get("growth", ""), future=u.get("future", ""), **feats, **extra))
    for p in PF_CAREERS:
        if p["id"] in used_pf:
            continue
        out.append(dict(id=p["id"], title=p["title"], source="pathfinder", in_ui=False,
                        category=p["category"], field=CATEGORY_TO_FIELD.get(p["category"], "other"),
                        description=p["description"], overview=p["description"],
                        roles=[], ui_skills=[], salary="", growth="", future="",
                        interests=p["interests"], skills=p["skills"],
                        subjects=[s.split("-")[0] for s in p["subject_codes"]], values=p["work_values"],
                        next_steps=p["next_steps"], resources=_resources(p["resources"])))
    return out


if __name__ == "__main__":
    cat = build_catalogue()
    print(len(cat), "careers;", sum(c["in_ui"] for c in cat), "in UI")
    for c in cat:
        print(f'{c["id"]:28} {c["source"]:10} {"".join(c["interests"]):3} {len(c["skills"])} {len(c["subjects"])} {len(c["values"])}')
