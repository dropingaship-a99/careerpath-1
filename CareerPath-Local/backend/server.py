"""CareerPath backend: PathFinder API + ML engine.   Run:  python server.py

Serves JSON only (the UI is the Next.js app in ../frontend). Listens on 127.0.0.1:8000
(set another port with PORT=9000). Needs only the Python standard library; numpy and
scikit-learn switch the ML model on (see requirements.txt).

Original PathFinder endpoints (unchanged): /api/questions /api/meta /api/careers
  /api/careers/{id} /api/subjects/search /api/resources /api/counsellors/nearby
  POST /api/careers/recommend
New endpoints:
  GET  /api/health          liveness check
  GET  /api/ml/status       model status, accuracy metrics, feedback count
  GET  /api/ml/catalogue    the unified career list the model knows
  POST /api/ml/recommend    {areas, interests, skills, subjects, values, goal} -> ranked careers
  POST /api/ml/feedback     {career_id, label: 1 | -1, profile} -> stored, model retrains
  POST /api/ml/retrain      retrain now
  POST /api/advisor         {question, profile} -> offline career-advisor answer
"""
import json
import os
import sys
import traceback
from http.server import ThreadingHTTPServer
from urllib.parse import urlparse

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
os.chdir(HERE)

import app as pathfinder                      # noqa: E402  (original PathFinder handlers)
from ml.engine import ML_AVAILABLE, get_engine  # noqa: E402

PORT = int(os.environ.get("BACKEND_PORT") or os.environ.get("PORT") or "8000")
MAX_BODY = 64 * 1024

LANDING = b"""<!doctype html><meta charset=utf-8><title>CareerPath API</title>
<body style="font-family:system-ui;max-width:42rem;margin:3rem auto;line-height:1.5">
<h1>CareerPath backend is running</h1>
<p>This is the API. Open the app at <a href="http://localhost:3000">http://localhost:3000</a>.</p>
<p>Check <a href="/api/health">/api/health</a> or <a href="/api/ml/status">/api/ml/status</a>.</p></body>"""


class Handler(pathfinder.Handler):
    def _json_body(self):
        try:
            size = int(self.headers.get("Content-Length", 0))
        except ValueError:
            raise ValueError("Bad Content-Length header.")
        if size > MAX_BODY:
            raise ValueError("Request is too large.")
        try:
            body = json.loads(self.rfile.read(size) or b"{}")
        except json.JSONDecodeError:
            raise ValueError("Request body must be valid JSON.")
        if not isinstance(body, dict):
            raise ValueError("Send a JSON object.")
        return body

    def _fail(self, code, msg):
        self.reply(code, {"error": msg})

    def do_GET(self):
        path = urlparse(self.path).path.rstrip("/") or "/"
        try:
            if path == "/":
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(LANDING)))
                self.end_headers()
                return self.wfile.write(LANDING)
            if path == "/api/health":
                return self.reply(200, {"status": "ok", "ml_available": ML_AVAILABLE})
            if path == "/api/ml/status":
                return self.reply(200, get_engine().status())
            if path == "/api/ml/catalogue":
                return self.reply(200, {"careers": [
                    {k: c[k] for k in ("id", "title", "category", "field", "in_ui", "source")}
                    for c in get_engine().catalogue]})
        except Exception:
            traceback.print_exc()
            return self._fail(500, "Something went wrong on the server.")
        return super().do_GET()

    def do_POST(self):
        path = urlparse(self.path).path.rstrip("/")
        routes = ("/api/ml/recommend", "/api/ml/feedback", "/api/ml/retrain", "/api/advisor")
        if path not in routes:
            return super().do_POST()
        try:
            engine = get_engine()
            body = self._json_body()
            if path == "/api/ml/recommend":
                return self.reply(200, engine.recommend(body.get("profile", body), top=int(body.get("top", 6))))
            if path == "/api/ml/feedback":
                return self.reply(200, engine.add_feedback(body.get("career_id"), body.get("label"),
                                                           body.get("profile")))
            if path == "/api/ml/retrain":
                if not ML_AVAILABLE:
                    raise ValueError("Install numpy and scikit-learn to enable the ML model.")
                engine.train()
                return self.reply(200, engine.status())
            return self.reply(200, {"answer": engine.advise(body.get("question"), body.get("profile"))})
        except (ValueError, TypeError) as e:
            self._fail(400, str(e))
        except Exception:
            traceback.print_exc()
            self._fail(500, "Something went wrong on the server.")

    def log_message(self, fmt, *args):
        if args and str(args[1]).startswith(("4", "5")):
            sys.stderr.write("[backend] %s\n" % (fmt % args))


def main():
    engine = get_engine()
    st = engine.status()
    if st["model_trained"]:
        m = st["metrics"]
        print(f"[backend] ML model ready: {m['careers_modelled']} careers, top-3 accuracy "
              f"{m['top3_accuracy']:.0%} on synthetic test set, {st['feedback_total']} feedback items.")
    else:
        print("[backend] numpy/scikit-learn not found: using rule-based matching only. "
              "Run: pip install -r requirements.txt")
    try:
        server = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    except OSError as e:
        sys.exit(f"[backend] Cannot use port {PORT} ({e}). Close the other program or run: PORT=8001 python server.py")
    print(f"[backend] API running at http://127.0.0.1:{PORT}  (Ctrl+C to stop)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[backend] stopped")


if __name__ == "__main__":
    main()
