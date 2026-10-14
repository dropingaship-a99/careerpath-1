"""Quick self-test of the ML backend:  python selftest.py   (takes about 10 seconds)."""
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ml.engine as M  # noqa: E402

M.FEEDBACK_FILE = os.path.join(tempfile.mkdtemp(), "feedback.jsonl")   # never touch real feedback
engine = M.get_engine()
failures = []


def check(name, ok, detail=""):
    print(("PASS  " if ok else "FAIL  ") + name + (f"  ({detail})" if detail and not ok else ""))
    if not ok:
        failures.append(name)


def top(profile, n=3):
    return [c["id"] for c in engine.recommend(profile, top=n)["careers"]]


def raises(fn):
    try:
        fn()
    except ValueError:
        return True
    return False


check("catalogue merges UI + PathFinder careers", len(engine.catalogue) >= 35 and sum(c["in_ui"] for c in engine.catalogue) >= 23)
check("ML available and trained" if M.ML_AVAILABLE else "ML libraries missing (rule-based mode)", engine.model is not None or not M.ML_AVAILABLE)
if engine.model is not None:
    check("synthetic top-3 accuracy above 70%", engine.metrics["top3_accuracy"] > 0.70, engine.metrics["top3_accuracy"])

tech = top({"areas": ["technology"], "skills": ["Coding", "Problem solving"], "subjects": ["Mathematics", "Computer Science"]})
check("tech profile -> a tech career on top", tech[0] in {"software-engineer", "data-scientist", "cybersecurity-analyst", "cloud-architect"}, tech)
law = top({"areas": ["law"], "skills": ["Communication"]}, 4)
check("law profile -> a legal career in top 4", any(c in law for c in ("corporate-lawyer", "judge", "legal-advisor", "criminal-lawyer")), law)
check("design profile -> the three design careers", set(top({"skills": ["Creativity & design"], "subjects": ["Art & Design"]})) == {"graphic-designer", "animator", "ux-ui-designer"})
quiz = {t: [2, 2, 2] if t == "S" else [0, 0, 0] for t in M.TYPES}
check("quiz input works (Helper-heavy)", engine.recommend({"interests": quiz})["profile"][0]["type"] == "S")

check("empty profile rejected", raises(lambda: engine.recommend({})))
check("bad quiz values rejected", raises(lambda: engine.recommend({"interests": {t: [9, 9, 9] for t in M.TYPES}})))
check("non-object profile rejected", raises(lambda: engine.recommend("x")))
check("unknown career feedback rejected", raises(lambda: engine.add_feedback("nope", 1, {"skills": ["Coding", "Research"]})))
check("thin-profile feedback rejected", raises(lambda: engine.add_feedback("doctor", 1, {"skills": ["Coding"]})))

p = {"areas": ["healthcare"], "skills": ["Helping people", "Research"], "subjects": ["Biology"]}
before = {c["id"]: c["match"] for c in engine.recommend(p, top=8)["careers"]}
for _ in range(M.RETRAIN_EVERY):
    engine.add_feedback("physiotherapist", 1, p)
engine.train()
after = {c["id"]: c["match"] for c in engine.recommend(p, top=8)["careers"]}
check("positive feedback raises that career's score", after.get("physiotherapist", 0) > before.get("physiotherapist", 0), (before.get("physiotherapist"), after.get("physiotherapist")))

check("advisor names the career", "Psychologist" in engine.advise("which subjects help for psychology?"))
check("advisor points to NCS for counselling", "ncs.gov.in" in engine.advise("how do I find a counsellor"))
check("advisor handles gibberish", "Try naming" in engine.advise("qwzx plmk"))

print("\nAll checks passed." if not failures else f"\n{len(failures)} check(s) failed: {failures}")
sys.exit(1 if failures else 0)
