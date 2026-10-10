import os
import re
import sqlite3
from functools import wraps
from pathlib import Path

from dotenv import load_dotenv

from flask import (
    Flask, flash, g, redirect, render_template, request, session, url_for
)
from flask_bcrypt import Bcrypt
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_wtf.csrf import CSRFProtect
from werkzeug.security import safe_join

BASE_DIR = Path(__file__).resolve().parent

load_dotenv(BASE_DIR / ".env")

DATABASE = BASE_DIR / "users.db"

app = Flask(__name__)
app.config.update(
    SECRET_KEY=os.environ.get("SECRET_KEY", ""),
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=os.environ.get("COOKIE_SECURE", "0") == "1",
    PERMANENT_SESSION_LIFETIME=1800,  # 30 minutes
    MAX_CONTENT_LENGTH=1 * 1024 * 1024,
)

# Fail closed rather than silently run with a predictable secret.
if not app.config["SECRET_KEY"]:
    raise RuntimeError(
        "SECRET_KEY is missing. Copy .env.example to .env and set a long random secret, "
        "then load it into your environment (see README.md)."
    )

bcrypt = Bcrypt(app)
csrf = CSRFProtect(app)
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=[],
    storage_uri="memory://",  # For a single-process classroom demo only.
)

def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db

@app.teardown_appcontext
def close_db(exception=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()

def init_db():
    with sqlite3.connect(DATABASE) as db:
        db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL COLLATE NOCASE UNIQUE,
                email TEXT NOT NULL COLLATE NOCASE UNIQUE,
                password_hash TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)
        db.commit()

def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("user_id"):
            flash("Please log in to view that page.", "info")
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapped

def valid_username(username):
    return bool(re.fullmatch(r"[A-Za-z0-9_]{3,24}", username))

def valid_email(email):
    # Basic classroom-level validation; production apps should also verify ownership.
    return bool(re.fullmatch(r"[^@\s]{1,64}@[^@\s.]+(?:\.[^@\s.]+)+", email))

@app.route("/")
def index():
    if session.get("user_id"):
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))

@app.route("/register", methods=["GET", "POST"])
@limiter.limit("5 per minute")
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        errors = []
        if not valid_username(username):
            errors.append("Username must be 3–24 characters and contain only letters, numbers, or underscores.")
        if len(email) > 254 or not valid_email(email):
            errors.append("Enter a valid email address.")
        if len(password) < 12 or len(password) > 72:
            errors.append("Password must be between 12 and 72 characters.")
        if password != confirm_password:
            errors.append("Passwords do not match.")

        if errors:
            for error in errors:
                flash(error, "error")
            return render_template("register.html"), 400

        password_hash = bcrypt.generate_password_hash(password).decode("utf-8")
        db = get_db()
        try:
            # Parameterized SQL prevents user input from becoming SQL code.
            db.execute(
                "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
                (username, email, password_hash),
            )
            db.commit()
        except sqlite3.IntegrityError:
            flash("That username or email is already registered.", "error")
            return render_template("register.html"), 409

        flash("Account created successfully. You can now log in.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
@limiter.limit("5 per minute")
def login():
    if request.method == "POST":
        identifier = request.form.get("identifier", "").strip()
        password = request.form.get("password", "")
        user = get_db().execute(
            "SELECT id, username, email, password_hash FROM users "
            "WHERE username = ? COLLATE NOCASE OR email = ? COLLATE NOCASE",
            (identifier, identifier),
        ).fetchone()

        # Keep the response generic so the page doesn't reveal whether an account exists.
        if user and bcrypt.check_password_hash(user["password_hash"], password):
            session.clear()  # Rotate session state on successful authentication.
            session.permanent = True
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            flash("Welcome back!", "success")
            return redirect(url_for("dashboard"))

        flash("Invalid username/email or password.", "error")
        return render_template("login.html"), 401

    return render_template("login.html")

@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html", username=session.get("username", "User"))

@app.route("/logout", methods=["POST"])
@login_required
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("login"))

@app.after_request
def add_security_headers(response):
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; style-src 'self'; img-src 'self' data:; "
        "form-action 'self'; frame-ancestors 'none'; base-uri 'self'"
    )
    response.headers["Cache-Control"] = "no-store"
    return response

# Create the database when the app starts.
init_db()

if __name__ == "__main__":
    # Debug mode is intentionally disabled. Use a production WSGI server for deployment.
    app.run(host="127.0.0.1", port=5000, debug=False)
