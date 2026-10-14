"""CareerPath ML engine.

What it does
------------
* Encodes a student profile (interest quiz or interest areas, skills, subjects, work values)
  into a 45-number feature vector.
* Scores every career in two ways and blends them:
    - RULE score: the transparent PathFinder formula
      (40% interests + 30% skills + 20% subjects + 10% values).
    - ML score: a multinomial Logistic Regression (scikit-learn) that predicts which career
      a profile belongs to. It is trained on synthetic student profiles generated from each
      career's feature profile, plus every piece of real feedback collected in
      data/feedback.jsonl (positive feedback is up-weighted).
* Feedback loop ("future accuracy"): thumbs up / down on a result is stored on disk and the
  model retrains automatically after a few new feedback items and on every start-up.
* Local advisor: TF-IDF retrieval over the catalogue to answer career questions offline.

Honest limits
-------------
The model is trained on synthetic data until real feedback arrives, so its reported
accuracy measures how well it recovers the catalogue's own profiles, NOT how well it predicts
a real student's success or satisfaction. Treat scores as exploratory guidance.

If numpy / scikit-learn are not installed the engine still works using the rule score only.
"""
import json
import os
import re
import threading
import time

from data.questions import NAMES, SKILLS, TYPES, VALUES
from data.subjects import SUBJECTS
from ml.catalogue import build_catalogue

try:
    import numpy as np
    from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS, TfidfVectorizer
    from sklearn.linear_model import LogisticRegression
    ML_AVAILABLE = True
except Exception:  # pragma: no cover - depends on the user's machine
    np = None
    ENGLISH_STOP_WORDS = frozenset()
    ML_AVAILABLE = False

HERE = os.path.dirname(os.path.abspath(__file__))
FEEDBACK_FILE = os.path.join(os.path.dirname(HERE), "data", "feedback.jsonl")

WEIGHTS = {"interests": 0.4, "skills": 0.3, "subjects": 0.2, "values": 0.1}
RULE_SHARE = 0.5           # final score = RULE_SHARE * rule + (1 - RULE_SHARE) * ml
RETRAIN_EVERY = 5          # retrain after this many new feedback items
POSITIVE_WEIGHT = 3.0      # one real "this fits me" counts as 3 synthetic samples

SKILL_KEYS = list(SKILLS)
SUBJECT_KEYS = [c.split("-")[0] for c in SUBJECTS]           # CS, BIO, ...
SUBJECT_NAMES = {c.split("-")[0]: v[0] for c, v in SUBJECTS.items()}
VALUE_KEYS = list(VALUES)
FEATURE_NAMES = ([f"{NAMES[t]} interest" for t in TYPES] + [SKILLS[k] for k in SKILL_KEYS]
                 + [SUBJECT_NAMES[k] for k in SUBJECT_KEYS] + [VALUES[k] for k in VALUE_KEYS])
N_FEATURES = len(FEATURE_NAMES)
_a, _b, _c = len(TYPES), len(TYPES) + len(SKILL_KEYS), len(TYPES) + len(SKILL_KEYS) + len(SUBJECT_KEYS)
GROUPS = ((0, _a), (_a, _b), (_b, _c), (_c, N_FEATURES))   # interests, skills, subjects, values

# Labels used by the UI's AI Career Lab -> backend keys
UI_SKILLS = {
    "problem solving": "problem", "coding": "coding", "maths & data": "maths", "writing": "writing",
    "creativity & design": "drawing", "helping people": "empathy", "research": "research",
    "leadership": "leadership", "communication": "speaking", "organising": "organising",
}
UI_SUBJECTS = {
    "mathematics": ["MATH"], "computer science": ["CS"], "physics": ["PHY"], "biology": ["BIO"],
    "chemistry": ["CHM"], "economics": ["ECO"], "business studies": ["BUS"], "psychology": ["PSY"],
    "english": ["ENG"], "art & design": ["ART", "DES"],
}
# UI "areas" -> how much they say about each RIASEC letter (when the quiz was not taken)
FIELD_TO_RIASEC = {
    "technology": {"I": 3, "C": 2, "R": 1}, "science": {"I": 3, "R": 2},
    "healthcare": {"S": 3, "I": 2}, "business": {"E": 3, "C": 2},
    "law": {"E": 2, "S": 2, "C": 2}, "other": {"A": 3, "S": 1, "E": 1},
}


# ---------------------------------------------------------------- text helpers
GENERIC_WORDS = set(ENGLISH_STOP_WORDS) | {
    "life", "career", "careers", "job", "jobs", "want", "become", "study", "learn", "start", "explore",
    "school", "help", "tell", "know", "like", "good", "best", "way", "ways", "subject", "subjects",
    "choose", "need", "work", "works", "working", "people", "does", "make", "makes", "stream", "class",
    "salary", "pay", "earn", "compare", "versus", "difference", "between", "about", "much", "many"}


def stems(text):
    """Very light stemmer: first 6 letters, so psychology == psychologist, animation == animator."""
    return [t[:6] for t in re.findall(r"[a-z]{3,}", text.lower()) if t not in GENERIC_WORDS]


# ---------------------------------------------------------------- profile handling
def _clean_list(v, limit=30):
    if not isinstance(v, list):
        return []
    return [x.strip() for x in v if isinstance(x, str) and x.strip()][:limit]


def normalise_profile(raw):
    """Turn whatever the UI sent into a clean profile. Raises ValueError for bad input."""
    if raw is None:
        raw = {}
    if not isinstance(raw, dict):
        raise ValueError("Profile must be a JSON object.")

    totals, given = {t: 0 for t in TYPES}, False
    areas = [a.lower().split()[0] for a in _clean_list(raw.get("areas")) if a.lower().split()[0] in FIELD_TO_RIASEC]
    quiz = raw.get("interests")
    if isinstance(quiz, dict) and quiz:
        for t in TYPES:
            vals = quiz.get(t)
            if not isinstance(vals, list) or len(vals) != 3 or any(v not in (0, 1, 2) for v in vals):
                raise ValueError(f"Quiz answers for type {t} must be three numbers, each 0, 1 or 2.")
            totals[t] = sum(vals)
        given = True
    else:
        for area in areas:
            for letter, pts in FIELD_TO_RIASEC[area].items():
                totals[letter] = min(6, totals[letter] + pts)
                given = True

    skills = set()
    for s in _clean_list(raw.get("skills")):
        key = UI_SKILLS.get(s.lower()) or (s.lower() if s.lower() in SKILLS else None)
        if key:
            skills.add(key)
    subjects = set()
    for s in _clean_list(raw.get("subjects")):
        if s.lower() in UI_SUBJECTS:
            subjects.update(UI_SUBJECTS[s.lower()])
        elif s.upper().split("-")[0] in SUBJECT_KEYS:
            subjects.add(s.upper().split("-")[0])
    values = {v.lower() for v in _clean_list(raw.get("values")) if v.lower() in VALUES}
    goal = raw.get("goal") if isinstance(raw.get("goal"), str) else ""
    return {"totals": totals, "interests_given": given, "areas": sorted(set(areas)), "skills": sorted(skills),
            "subjects": sorted(subjects), "values": sorted(values), "goal": goal.strip()[:500]}


def encode(p):
    """Profile -> list of N_FEATURES numbers between 0 and 1."""
    x = [p["totals"][t] / 6 for t in TYPES]
    x += [1.0 if k in p["skills"] else 0.0 for k in SKILL_KEYS]
    x += [1.0 if k in p["subjects"] else 0.0 for k in SUBJECT_KEYS]
    x += [1.0 if k in p["values"] else 0.0 for k in VALUE_KEYS]
    return x


def signal_count(p):
    return int(p["interests_given"]) + len(p["skills"]) + len(p["subjects"]) + len(p["values"])


# ---------------------------------------------------------------- engine
class Engine:
    def __init__(self):
        self.lock = threading.RLock()
        self.catalogue = build_catalogue()
        self.by_id = {c["id"]: c for c in self.catalogue}
        self.featured = [c for c in self.catalogue if c["interests"]]   # careers the model can learn
        self.model = None
        self.classes = []
        self.metrics = {}
        self.trained_at = None
        self.trained_on_feedback = 0
        self.feedback = self._load_feedback()
        self.since_retrain = 0
        self._docs = [self._doc(c) for c in self.catalogue]
        self.tfidf = self.doc_matrix = None
        if ML_AVAILABLE:
            self.tfidf = TfidfVectorizer(analyzer=stems, sublinear_tf=True)
            self.doc_matrix = self.tfidf.fit_transform(self._docs)
            self.train()

    # ---------- catalogue helpers
    @staticmethod
    def _doc(c):
        parts = [c["title"], c["title"], c["category"], c["description"], c["overview"], " ".join(c["roles"]),
                 " ".join(c["ui_skills"]), " ".join(SKILLS[s] for s in c["skills"]),
                 " ".join(SUBJECT_NAMES[s] for s in c["subjects"] if s in SUBJECT_NAMES),
                 " ".join(VALUES[v] for v in c["values"]), " ".join(c["next_steps"])]
        return " ".join(parts)

    # ---------- synthetic data + training
    def _synthetic(self, per_career, seed):
        """Simulated students per career, shaped like real UI input: students tick only a few
        items (mostly from the career's traits, sometimes unrelated ones), interests
        come either from the 18-question quiz or from chosen areas, and whole groups are
        sometimes left blank."""
        rng = np.random.default_rng(seed)

        def pick(pool, traits):
            # each trait is ticked with 40% chance, every other option with 8%: students tick
            # a few items, and careers with more listed traits are not unfairly penalised
            return [k for k in pool if rng.random() < (0.40 if k in traits else 0.08)]

        X, y = [], []
        for ci, c in enumerate(self.featured):
            first, second = c["interests"][0], (c["interests"] + [c["interests"][0]])[1]
            for _ in range(per_career):
                totals = {t: 0 for t in TYPES}
                if rng.random() < 0.5:                       # 18-question quiz
                    totals = {t: int(rng.integers(0, 4)) for t in TYPES}
                    totals[first] = int(rng.integers(3, 7))
                    totals[second] = max(totals[second], int(rng.integers(2, 6)))
                    if rng.random() < 0.12:                  # the student mixes up the top two
                        totals[first], totals[second] = totals[second], totals[first]
                else:                                        # "areas" chips in the Career Lab
                    areas = [c["field"]] if rng.random() < 0.8 else []
                    if rng.random() < 0.3:
                        areas.append(list(FIELD_TO_RIASEC)[int(rng.integers(len(FIELD_TO_RIASEC)))])
                    for a in set(areas):
                        for letter, pts in FIELD_TO_RIASEC[a].items():
                            totals[letter] = min(6, totals[letter] + pts)
                p = {"totals": totals}
                p["skills"] = pick(SKILL_KEYS, c["skills"])
                p["subjects"] = pick(SUBJECT_KEYS, c["subjects"])
                p["values"] = pick(VALUE_KEYS, c["values"])
                x = encode(p)
                for lo, hi in GROUPS:                        # whole group left blank
                    if rng.random() < 0.15:
                        x[lo:hi] = [0.0] * (hi - lo)
                X.append(x)
                y.append(ci)
        return np.array(X), np.array(y)

    def train(self):
        """(Re)train on synthetic data + real feedback; evaluate on a fresh synthetic test set."""
        if not ML_AVAILABLE:
            return
        with self.lock:
            t0 = time.time()
            ids = [c["id"] for c in self.featured]
            X, y = self._synthetic(250, seed=7)
            w = np.ones(len(y))
            real = [f for f in self.feedback if f["label"] > 0 and f["career_id"] in ids
                    and len(f.get("x", [])) == N_FEATURES]
            if real:
                X = np.vstack([X, np.array([f["x"] for f in real])])
                y = np.concatenate([y, np.array([ids.index(f["career_id"]) for f in real])])
                w = np.concatenate([w, np.full(len(real), POSITIVE_WEIGHT)])
            model = LogisticRegression(C=1.0, max_iter=3000)
            model.fit(X, y, sample_weight=w)

            Xt, yt = self._synthetic(60, seed=99)
            proba = model.predict_proba(Xt)
            order = np.argsort(-proba, axis=1)
            acc = lambda k: float(np.mean([yt[i] in order[i, :k] for i in range(len(yt))]))
            self.model, self.classes = model, ids
            self.trained_on_feedback = len(real)
            self.since_retrain = 0
            self.trained_at = time.strftime("%Y-%m-%d %H:%M:%S")
            self.metrics = {
                "top1_accuracy": round(acc(1), 3), "top3_accuracy": round(acc(3), 3),
                "top5_accuracy": round(acc(5), 3), "test_samples": int(len(yt)),
                "train_samples": int(len(y)), "careers_modelled": len(ids),
                "real_feedback_used": len(real), "train_seconds": round(time.time() - t0, 2),
                "note": ("Measured on synthetic students generated from the catalogue, so it shows "
                         "consistency with the catalogue, not real-world prediction accuracy."),
            }

    # ---------- feedback
    def _load_feedback(self):
        out = []
        try:
            with open(FEEDBACK_FILE, encoding="utf-8") as f:
                for line in f:
                    try:
                        item = json.loads(line)
                        if isinstance(item, dict) and item.get("label") in (1, -1):
                            out.append(item)
                    except ValueError:
                        continue  # skip a damaged line instead of crashing
        except OSError:
            pass
        return out

    def add_feedback(self, career_id, label, raw_profile):
        if career_id not in self.by_id:
            raise ValueError("Unknown career id.")
        if label not in (1, -1):
            raise ValueError("'label' must be 1 (fits me) or -1 (does not fit).")
        profile = normalise_profile(raw_profile)
        if signal_count(profile) < 2:
            raise ValueError("Answer at least two questions before sending feedback.")
        item = {"ts": time.strftime("%Y-%m-%d %H:%M:%S"), "career_id": career_id, "label": label,
                "x": [round(v, 4) for v in encode(profile)]}
        with self.lock:
            self.feedback.append(item)
            try:
                with open(FEEDBACK_FILE, "a", encoding="utf-8") as f:
                    f.write(json.dumps(item) + "\n")
            except OSError:
                pass  # feedback still counts for this session
            self.since_retrain += 1
            retrain = ML_AVAILABLE and self.since_retrain >= RETRAIN_EVERY
        if retrain:
            threading.Thread(target=self.train, daemon=True).start()
        return {"saved": True, "feedback_total": len(self.feedback),
                "retrain_in": 0 if retrain else max(0, RETRAIN_EVERY - self.since_retrain)}

    def _feedback_multiplier(self, career_id):
        up = sum(1 for f in self.feedback if f["career_id"] == career_id and f["label"] > 0)
        down = sum(1 for f in self.feedback if f["career_id"] == career_id and f["label"] < 0)
        return 1 + 0.25 * (up - down) / (up + down + 4)       # always between 0.75 and 1.25

    # ---------- scoring
    @staticmethod
    def _overlap(chosen, wanted):
        """Share of the career's traits the student covers. A career counts as fully matched once
        the student covers 3 of its traits, so careers with many listed traits are not penalised."""
        if not chosen or not wanted:
            return 0.5
        return len(set(chosen) & set(wanted)) / min(len(wanted), max(len(chosen), 3))

    def _rule_parts(self, p, c):
        if p["interests_given"] and c["interests"]:
            first, second = (c["interests"] + [c["interests"][0]])[:2]
            interests = (2 * p["totals"][first] + p["totals"][second]) / 18
        else:
            interests = 0.5
        return {"interests": min(1.0, interests),
                "skills": self._overlap(p["skills"], c["skills"]),
                "subjects": self._overlap(p["subjects"], c["subjects"]),
                "values": self._overlap(p["values"], c["values"])}

    def _text_scores(self, text):
        if not (ML_AVAILABLE and text.strip()):
            return None
        sims = (self.doc_matrix @ self.tfidf.transform([text]).T).toarray().ravel()
        top = float(sims.max())
        return sims / top if top > 0 else None

    def recommend(self, raw_profile, top=6):
        p = normalise_profile(raw_profile)
        if signal_count(p) == 0 and not p["goal"]:
            raise ValueError("Choose at least one interest, skill or subject (or describe your goal).")
        x = encode(p)
        ml = {}
        contrib = None
        with self.lock:
            if self.model is not None:
                proba = self.model.predict_proba(np.array([x]))[0]
                pmax = float(proba.max()) or 1.0
                ml = {cid: float(pr) for cid, pr in zip(self.classes, proba)}
                xs = np.array(x)
                contrib = {cid: self.model.coef_[i] * xs for i, cid in enumerate(self.classes)}
            else:
                pmax = 1.0
        text = self._text_scores(p["goal"])

        results = []
        for i, c in enumerate(self.catalogue):
            parts = self._rule_parts(p, c)
            rule = sum(WEIGHTS[k] * parts[k] for k in WEIGHTS)
            if c["id"] in ml:
                # square root keeps one very confident class from drowning out the others
                score = RULE_SHARE * rule + (1 - RULE_SHARE) * (ml[c["id"]] / pmax) ** 0.5
            else:
                score = rule
            if p["areas"]:
                score = 0.85 * score + 0.15 * (1.0 if c["field"] in p["areas"] else 0.0)
            if text is not None:
                score = 0.85 * score + 0.15 * float(text[i])
            score *= self._feedback_multiplier(c["id"])
            results.append((min(score, 1.0), rule, parts, c))
        results.sort(key=lambda r: -r[0])

        out = []
        for score, rule, parts, c in results[:top]:
            out.append({
                "id": c["id"], "title": c["title"], "in_ui": c["in_ui"], "category": c["category"],
                "description": c["description"], "match": round(score * 100),
                "rule_score": round(rule * 100),
                "ml_probability": round(ml.get(c["id"], 0.0) * 100, 1) if ml else None,
                "breakdown": {k: round(v * 100) for k, v in parts.items()},
                "reasons": self._reasons(p, c, parts, contrib.get(c["id"]) if contrib else None),
                "next_steps": c["next_steps"], "resources": c["resources"],
                "subjects": [SUBJECT_NAMES[s] for s in c["subjects"] if s in SUBJECT_NAMES],
            })
        n = signal_count(p)
        top_types = sorted(TYPES, key=lambda t: (-p["totals"][t], TYPES.index(t)))[:3] if p["interests_given"] else []
        return {
            "careers": out,
            "profile": [{"type": t, "name": NAMES[t], "score": p["totals"][t]} for t in top_types],
            "engine": {"ml_active": self.model is not None, "signals": n,
                       "confidence_note": ("Add more answers (skills, subjects, interests) for a more reliable "
                                           "ranking." if n < 4 else ""),
                       "feedback_total": len(self.feedback)},
        }

    def _reasons(self, p, c, parts, contrib):
        r = []
        if c["field"] in p["areas"]:
            r.append(f"Falls in the {c['field'].capitalize()} area you chose")
        if p["interests_given"] and c["interests"] and parts["interests"] >= 0.5:
            r.append(f"Matches your {NAMES[c['interests'][0]]} interest")
        sk = [SKILLS[s] for s in c["skills"] if s in p["skills"]]
        if sk:
            r.append("Uses your skills: " + ", ".join(sk).lower())
        sb = [SUBJECT_NAMES[s] for s in c["subjects"] if s in p["subjects"]]
        if sb:
            r.append("Builds on subjects you like: " + ", ".join(sb))
        vl = [VALUES[v] for v in c["values"] if v in p["values"]]
        if vl:
            r.append("Fits what you value: " + ", ".join(vl).lower())
        if contrib is not None:
            idx = [i for i in np.argsort(-contrib)[:3] if contrib[i] > 0.05]
            if idx:
                r.append("Strongest ML signals: " + ", ".join(FEATURE_NAMES[i] for i in idx))
        return r or ["Worth a quick look alongside your other options."]

    # ---------- status
    def status(self):
        return {"ml_available": ML_AVAILABLE, "model_trained": self.model is not None,
                "trained_at": self.trained_at, "metrics": self.metrics,
                "feedback_total": len(self.feedback), "careers": len(self.catalogue),
                "retrain_every": RETRAIN_EVERY,
                "install_hint": None if ML_AVAILABLE else "pip install numpy scikit-learn"}

    # ---------- local advisor (no API key needed)
    def advise(self, question, profile_raw=None):
        q = (question or "").strip()
        if not q:
            raise ValueError("Ask a question first.")
        lower = q.lower()
        parts = []
        wants_counsellor = bool(re.search(r"counsel|guidance|helpline|talk to (someone|a person)", lower))
        if wants_counsellor:
            parts.append("For free, personal guidance in India, the National Career Service (https://www.ncs.gov.in/, "
                         "toll-free 1800-425-1514) offers career counselling. Your school counsellor is another good start.")
        hits = [] if wants_counsellor else self._related(q, 2)

        asks_for_picks = re.search(r"which career|what career|career for me|suit me|fit me|suggest|recommend|"
                                   r"what should i (do|become|study)|what to become", lower)
        if asks_for_picks and not hits:
            try:
                rec = self.recommend(profile_raw, top=3)
                names = ", ".join(f"{r['title']} ({r['match']}%)" for r in rec["careers"])
                parts.append(f"From the answers you gave in the Career Lab, the closest matches right now are: {names}. "
                             "These are starting points to explore, not a verdict.")
            except ValueError:
                parts.append("Pick some interests, skills or subjects in the Career Lab above and I can rank careers for you.")

        if hits:
            parts.append(self._career_brief(hits[0], lower))
            if len(hits) > 1 and re.search(r"\b(vs|versus|compare|or|difference|between)\b", lower):
                parts.append("Compared with that, " + self._career_brief(hits[1], lower, short=True))
        elif not parts:
            parts.append("I can answer questions about the careers in this app, for example what a Data Scientist does, "
                         "which subjects help for Psychology, or how to start exploring Graphic Design. "
                         "Try naming a career, subject or skill.")
        parts.append("This is a local guide built from the app's own career data, not a live AI model. "
                     "Please check eligibility, admissions and licensing with official sources or a counsellor.")
        return "\n\n".join(parts)

    def _related(self, text, n):
        """Careers named in the question first (in the order they appear), then TF-IDF matches."""
        lower = text.lower()
        named = []
        for c in self.catalogue:
            names = {c["title"].lower(), c["id"].replace("-", " ")}
            pos = [lower.find(x) for x in names if x in lower]
            if pos:
                named.append((min(pos), c))
        named = [c for _, c in sorted(named, key=lambda t: t[0])]
        if len(named) >= n:
            return named[:n]
        if not ML_AVAILABLE:
            words = set(stems(lower))
            scored = sorted(((len(words & set(stems(d))), i) for i, d in enumerate(self._docs)), reverse=True)
            extra = [self.catalogue[i] for s, i in scored if s >= 2]
        else:
            sims = (self.doc_matrix @ self.tfidf.transform([text]).T).toarray().ravel()
            extra = [self.catalogue[i] for i in np.argsort(-sims) if sims[i] >= 0.12]
        return (named + [c for c in extra if c not in named])[:n]

    def _career_brief(self, c, lower, short=False):
        text = f"{c['title']}: {c['overview'] or c['description']}"
        if short:
            return text
        lines = [text]
        if c["roles"]:
            lines.append("• Typical roles: " + ", ".join(c["roles"][:5]))
        skills = c["ui_skills"] or [SKILLS[s] for s in c["skills"]]
        if skills:
            lines.append("• Key skills: " + ", ".join(skills))
        if re.search(r"\b(subject|stream|class|combination|choose|study)\b", lower) and c["subjects"]:
            lines.append("• Helpful school subjects: " + ", ".join(SUBJECT_NAMES[s] for s in c["subjects"] if s in SUBJECT_NAMES))
        if re.search(r"\b(salary|pay|earn|income|lpa)\b", lower) and c["salary"]:
            lines.append(f"• Typical pay shown in this app: {c['salary']} (varies a lot by employer and experience)")
        if c["growth"]:
            lines.append(f"• Outlook in this app's data: {c['growth']}")
        if c["next_steps"]:
            lines.append("• Ways to start: " + "; ".join(c["next_steps"][:3]))
        else:
            lines.append("• Ways to start: talk to someone working in this field, and try a free beginner course "
                         "in its key skills.")
        if c["resources"]:
            lines.append("• Free resources: " + ", ".join(f"{r['label']} ({r['url']})" for r in c["resources"][:3]))
        return "\n".join(lines)


_engine = None
_engine_lock = threading.Lock()


def get_engine():
    global _engine
    with _engine_lock:
        if _engine is None:
            _engine = Engine()
        return _engine
