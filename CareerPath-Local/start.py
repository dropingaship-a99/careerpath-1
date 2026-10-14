#!/usr/bin/env python3
"""Start CareerPath locally with one command:   python start.py

  1. installs the ML libraries (numpy, scikit-learn) if they are missing
  2. installs the UI packages (npm install / pnpm install) the first time
  3. starts the Python ML backend  -> http://127.0.0.1:8000
  4. starts the Next.js UI         -> http://localhost:3000   and opens it in your browser

Options:   --backend-only   run only the Python API (no Node.js needed)
           --no-browser     do not open the browser automatically
Ctrl+C stops everything.
"""
import json
import os
import shutil
import signal
import socket
import subprocess
import sys
import time
import urllib.request
import webbrowser

ROOT = os.path.dirname(os.path.abspath(__file__))
BACKEND = os.path.join(ROOT, "backend")
FRONTEND = os.path.join(ROOT, "frontend")
IS_WINDOWS = os.name == "nt"
children = []


def say(msg):
    print(f"[start] {msg}", flush=True)


def port_free(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.5)
        return s.connect_ex(("127.0.0.1", port)) != 0


def pick_port(preferred):
    for port in range(preferred, preferred + 20):
        if port_free(port):
            return port
    sys.exit(f"[start] No free port found near {preferred}. Close other programs and try again.")


def run_quiet(cmd, cwd=None):
    return subprocess.run(cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)


def ensure_python_packages():
    try:
        import numpy  # noqa: F401
        import sklearn  # noqa: F401
        return True
    except ImportError:
        pass
    say("Installing the ML libraries (numpy, scikit-learn). This happens once...")
    cmd = [sys.executable, "-m", "pip", "install", "-r", os.path.join(BACKEND, "requirements.txt")]
    result = subprocess.run(cmd)
    if result.returncode != 0:
        say("Could not install the ML libraries automatically. The app still works with rule-based "
            "matching only. To enable ML later run:  pip install -r backend/requirements.txt")
        return False
    return True


def node_ok():
    node = shutil.which("node")
    if not node:
        return False, "Node.js was not found"
    out = run_quiet([node, "--version"]).stdout.strip().lstrip("v")
    try:
        major, minor = (int(x) for x in out.split(".")[:2])
    except ValueError:
        return True, out
    if (major, minor) < (20, 9):
        return False, f"Node.js {out} is too old (need 20.9 or newer)"
    return True, out


def package_manager():
    """pnpm when available (the project ships a pnpm lockfile), otherwise npm."""
    if shutil.which("pnpm") and os.path.exists(os.path.join(FRONTEND, "pnpm-lock.yaml")):
        return shutil.which("pnpm")
    return shutil.which("npm")


def popen(cmd, cwd, env):
    kwargs = {}
    if not IS_WINDOWS:
        kwargs["start_new_session"] = True
    p = subprocess.Popen(cmd, cwd=cwd, env=env, **kwargs)
    children.append(p)
    return p


def stop_all():
    for p in children:
        if p.poll() is not None:
            continue
        try:
            if IS_WINDOWS:
                subprocess.run(["taskkill", "/PID", str(p.pid), "/T", "/F"], stdout=subprocess.DEVNULL,
                               stderr=subprocess.DEVNULL)
            else:
                os.killpg(os.getpgid(p.pid), signal.SIGTERM)
        except (OSError, ProcessLookupError):
            pass
    for p in children:
        try:
            p.wait(timeout=8)
        except subprocess.TimeoutExpired:
            p.kill()


def wait_for(url, proc, seconds, what):
    deadline = time.time() + seconds
    while time.time() < deadline:
        if proc.poll() is not None:
            return False
        try:
            with urllib.request.urlopen(url, timeout=2) as r:
                if r.status < 500:
                    return True
        except Exception:
            time.sleep(0.7)
    say(f"{what} did not answer within {seconds} seconds.")
    return False


def main():
    args = set(sys.argv[1:])
    if sys.version_info < (3, 8):
        sys.exit("[start] Python 3.8 or newer is required.")

    ensure_python_packages()

    backend_port = pick_port(int(os.environ.get("BACKEND_PORT", "8000")))
    env = dict(os.environ)
    env.pop("PORT", None)  # PORT would clash between the two servers
    env["BACKEND_PORT"] = str(backend_port)
    say(f"Starting the ML backend on port {backend_port}...")
    backend = popen([sys.executable, os.path.join(BACKEND, "server.py")], BACKEND, env)
    if not wait_for(f"http://127.0.0.1:{backend_port}/api/health", backend, 90, "The backend"):
        stop_all()
        sys.exit("[start] The backend failed to start. Read the messages above for the reason.")
    say("Backend is ready.")

    if "--backend-only" in args:
        say(f"Backend-only mode. API: http://127.0.0.1:{backend_port}/api/ml/status   (Ctrl+C to stop)")
        return supervise(None)

    ok, info = node_ok()
    if not ok:
        say(f"{info}. Install Node.js 20.9+ from https://nodejs.org to see the UI.")
        say(f"Meanwhile the backend keeps running at http://127.0.0.1:{backend_port}")
        return supervise(None)

    pm = package_manager()
    if not pm:
        stop_all()
        sys.exit("[start] npm was not found. Reinstall Node.js from https://nodejs.org")
    if not os.path.isdir(os.path.join(FRONTEND, "node_modules")):
        say("Installing the UI packages (first run only, needs internet, can take a few minutes)...")
        if subprocess.run([pm, "install"], cwd=FRONTEND, env=env).returncode != 0:
            stop_all()
            sys.exit("[start] Package installation failed. Check your internet connection, then run "
                     "'npm install' inside the frontend folder and start again.")

    frontend_port = pick_port(int(os.environ.get("FRONTEND_PORT", "3000")))
    env["BACKEND_URL"] = f"http://127.0.0.1:{backend_port}"
    say(f"Starting the UI on port {frontend_port}...")
    frontend = popen([pm, "run", "dev", "--", "-p", str(frontend_port)], FRONTEND, env)
    url = f"http://localhost:{frontend_port}"
    if wait_for(url, frontend, 180, "The UI"):
        say(f"CareerPath is ready:  {url}   (Ctrl+C to stop)")
        if "--no-browser" not in args:
            webbrowser.open(url)
    else:
        say("The UI did not start. Read the messages above for the reason.")
    return supervise(frontend)


def supervise(frontend):
    try:
        while True:
            time.sleep(1)
            if children and children[0].poll() is not None:
                say("The backend stopped unexpectedly.")
                break
            if frontend is not None and frontend.poll() is not None:
                say("The UI stopped.")
                break
    except KeyboardInterrupt:
        print()
        say("Stopping...")
    finally:
        stop_all()


if __name__ == "__main__":
    main()
