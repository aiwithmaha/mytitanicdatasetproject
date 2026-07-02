import os
import time
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, jsonify, request, send_from_directory
from werkzeug.security import check_password_hash

LOGIN_DIR = Path(__file__).resolve().parent
load_dotenv(LOGIN_DIR.parent / ".env")

app = Flask(__name__)

LOGIN_USERNAME = os.environ.get("LOGIN_USERNAME", "")
LOGIN_PASSWORD_HASH = os.environ.get("LOGIN_PASSWORD_HASH", "")

MIN_PASSWORD_LENGTH = 8
MAX_INPUT_LENGTH = 254

RATE_LIMIT_WINDOW_SECONDS = 60
RATE_LIMIT_MAX_ATTEMPTS = 5
_attempts_by_ip: dict[str, list[float]] = {}


def _is_rate_limited(ip: str) -> bool:
    now = time.time()
    recent = [t for t in _attempts_by_ip.get(ip, []) if now - t < RATE_LIMIT_WINDOW_SECONDS]
    _attempts_by_ip[ip] = recent
    return len(recent) >= RATE_LIMIT_MAX_ATTEMPTS


def _record_attempt(ip: str) -> None:
    _attempts_by_ip.setdefault(ip, []).append(time.time())


@app.get("/")
def index():
    return send_from_directory(LOGIN_DIR, "index.html")


@app.get("/style.css")
def style():
    return send_from_directory(LOGIN_DIR, "style.css")


@app.get("/script.js")
def script():
    return send_from_directory(LOGIN_DIR, "script.js")


@app.post("/login")
def login():
    if not LOGIN_USERNAME or not LOGIN_PASSWORD_HASH:
        return jsonify(success=False, message="Server is not configured."), 500

    client_ip = request.remote_addr or "unknown"
    if _is_rate_limited(client_ip):
        return jsonify(success=False, message="Too many attempts. Try again later."), 429

    payload = request.get_json(silent=True) or {}
    username = str(payload.get("username") or payload.get("email") or "").strip()
    password = payload.get("password") or ""

    valid_shape = (
        0 < len(username) <= MAX_INPUT_LENGTH
        and isinstance(password, str)
        and len(password) >= MIN_PASSWORD_LENGTH
    )
    if not valid_shape:
        _record_attempt(client_ip)
        return jsonify(success=False, message="Invalid credentials."), 401

    # Always run check_password_hash, even on a username mismatch, so a
    # wrong username and a wrong password take the same code path/timing
    # and an attacker can't use response time to enumerate usernames.
    if username == LOGIN_USERNAME:
        password_ok = check_password_hash(LOGIN_PASSWORD_HASH, password)
    else:
        check_password_hash(LOGIN_PASSWORD_HASH, password)
        password_ok = False

    if not password_ok:
        _record_attempt(client_ip)
        return jsonify(success=False, message="Invalid credentials."), 401

    return jsonify(success=True, message="Login successful."), 200


if __name__ == "__main__":
    app.run(debug=False)
