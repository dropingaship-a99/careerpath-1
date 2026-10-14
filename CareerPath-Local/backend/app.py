"""PathFinder server. Run:  python app.py   then open http://localhost:8000
Uses only the Python standard library. OWNER: Member 1 (Backend/API)."""

import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

from data.careers import CAREERS, CATEGORIES, RESOURCES
from data.questions import SKILLS, VALUES, NAMES, DESC, question_list
from data.subjects import COMBOS, SUBJECTS
from scoring import format_career, recommend

HERE = os.path.dirname(os.path.abspath(__file__))
STATIC = os.path.join(HERE, "static")
PORT = int(os.environ.get("PORT", "8000"))
TYPES_MIME = {".html": "text/html", ".css": "text/css", ".js": "application/javascript"}

NATIONAL = {
    "name": "National Career Service (Government of India)",
    "website": "https://www.ncs.gov.in/",
    "toll_free": "1800-425-1514",
    "note": "Free career counselling and Model Career Centres. Number as listed by NCS.",
}


def by_id(cid):
    return next((c for c in CAREERS if c["id"] == cid), None)


def list_careers(q):
    """Filters: q (keyword), category, interest (R/I/A/S/E/C), skill, subject (code), value."""
    get = lambda k: (q.get(k) or [""])[0].strip().lower()
    word, cat, interest = get("q"), get("category"), get("interest")
    skill, subject, value = get("skill"), get("subject"), get("value")
    out = []
    for c in CAREERS:
        text = " ".join([c["title"], c["description"], c["category"]] +
                        [SUBJECTS[s][0] for s in c["subject_codes"]] +
                        [SKILLS[s] for s in c["skills"]]).lower()
        if word and word not in text:
            continue
        if cat and c["category"].lower() != cat:
            continue
        if interest and interest.upper() not in c["interests"]:
            continue
        if skill and skill not in c["skills"]:
            continue
        if subject and subject.upper() not in c["subject_codes"]:
            continue
        if value and value not in c["work_values"]:
            continue
        out.append(format_career(c))
    return out


def search_subjects(term):
    term = term.strip().lower().replace(" ", "")
    out = []
    for code, (name, desc, skills, res, words) in SUBJECTS.items():
        hay = (code + name + words).lower().replace(" ", "")
        if term and term not in hay:
            continue
        out.append({
            "code": code, "name": name, "description": desc, "skills": skills,
            "careers": [{"id": c["id"], "title": c["title"]} for c in CAREERS if code in c["subject_codes"]],
            "resources": [{"label": RESOURCES[k][0], "url": RESOURCES[k][1]} for k in res],
            "combos": COMBOS.get(code, []),
        })
    return out


def resources_for(interest, skill):
    seen, out = set(), []
    for c in CAREERS:
        if interest and interest.upper() not in c["interests"]:
            continue
        if skill and skill.lower() not in c["skills"]:
            continue
        for k in c["resources"]:
            if k not in seen:
                seen.add(k)
                out.append({"label": RESOURCES[k][0], "url": RESOURCES[k][1]})
    return out


def counsellors_near(city, state):
    """Only shows people listed in data/counsellors.json who are verified AND gave consent."""
    if not city:
        raise ValueError("Please enter a city.")
    try:
        with open(os.path.join(HERE, "data", "counsellors.json"), encoding="utf-8") as f:
            people = json.load(f)
    except (OSError, ValueError):
        people = []
    hits = [p for p in people if p.get("verified") and p.get("consent")
            and p.get("city", "").lower() == city.lower()
            and (not state or p.get("state", "").lower() == state.lower())]
    msg = ("" if hits else
           "We do not have verified, consent-based counsellor details for this place yet. "
           "We only show contact details that are verified and shared with permission. "
           "Please use the National Career Service below.")
    return {"counsellors": hits, "national": NATIONAL, "message": msg}


def parse_picks(body):
    picks = {}
    for key, allowed in (("subjects", SUBJECTS), ("skills", SKILLS), ("values", VALUES)):
        vals = body.get(key, [])
        if not isinstance(vals, list) or any(v not in allowed for v in vals):
            raise ValueError(f"'{key}' must be a list of valid options.")
        picks[key] = vals
    return picks


class Handler(BaseHTTPRequestHandler):
    def reply(self, code, obj):
        data = json.dumps(obj).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        url = urlparse(self.path)
        path, q = url.path.rstrip("/") or "/", parse_qs(url.query)
        try:
            if path == "/api":
                return self.reply(200, {"app": "PathFinder", "status": "ok"})
            if path == "/api/questions":
                return self.reply(200, {
                    "interest": question_list(),
                    "subjects": [{"code": c, "name": s[0]} for c, s in SUBJECTS.items()],
                    "skills": [{"key": k, "label": v} for k, v in SKILLS.items()],
                    "values": [{"key": k, "label": v} for k, v in VALUES.items()],
                    "types": [{"type": t, "name": NAMES[t], "text": DESC[t]} for t in NAMES]})
            if path == "/api/meta":
                return self.reply(200, {
                    "categories": CATEGORIES,
                    "subjects": [{"code": c, "name": s[0]} for c, s in SUBJECTS.items()],
                    "skills": [{"key": k, "label": v} for k, v in SKILLS.items()],
                    "values": [{"key": k, "label": v} for k, v in VALUES.items()],
                    "interests": [{"key": t, "label": n} for t, n in NAMES.items()]})
            if path == "/api/careers":
                return self.reply(200, {"careers": list_careers(q)})
            if path.startswith("/api/careers/"):
                c = by_id(path.split("/")[-1])
                if not c:
                    return self.reply(404, {"error": "Career not found."})
                return self.reply(200, format_career(c))
            if path == "/api/subjects/search":
                return self.reply(200, {"subjects": search_subjects((q.get("q") or [""])[0])})
            if path == "/api/resources":
                return self.reply(200, {"resources": resources_for((q.get("interest") or [""])[0],
                                                                   (q.get("skill") or [""])[0])})
            if path == "/api/counsellors/nearby":
                return self.reply(200, counsellors_near((q.get("city") or [""])[0].strip(),
                                                        (q.get("state") or [""])[0].strip()))
            if path.startswith("/api/"):
                return self.reply(404, {"error": "Unknown API endpoint."})
            return self.static(path)
        except ValueError as e:
            self.reply(400, {"error": str(e)})
        except Exception:
            self.reply(500, {"error": "Something went wrong on the server."})

    def do_POST(self):
        path = urlparse(self.path).path.rstrip("/")
        if path not in ("/api/careers/recommend", "/api/recommend"):
            return self.reply(404, {"error": "Unknown API endpoint."})
        try:
            size = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(size) or b"{}")
            if not isinstance(body, dict):
                raise ValueError("Send a JSON object.")
            result = recommend(body.get("interests"), parse_picks(body))
            self.reply(200, result)
        except json.JSONDecodeError:
            self.reply(400, {"error": "Request body must be valid JSON."})
        except ValueError as e:
            self.reply(400, {"error": str(e)})
        except Exception:
            self.reply(500, {"error": "Something went wrong on the server."})

    def static(self, path):
        name = "index.html" if path == "/" else path.lstrip("/")
        full = os.path.realpath(os.path.join(STATIC, name))
        ext = os.path.splitext(full)[1]
        if not full.startswith(STATIC + os.sep) or ext not in TYPES_MIME or not os.path.isfile(full):
            return self.reply(404, {"error": "Page not found."})
        with open(full, "rb") as f:
            data = f.read()
        self.send_response(200)
        self.send_header("Content-Type", TYPES_MIME[ext] + "; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, fmt, *args):
        pass


if __name__ == "__main__":
    print(f"PathFinder running at http://localhost:{PORT}  (Ctrl+C to stop)")
    ThreadingHTTPServer(("", PORT), Handler).serve_forever()
