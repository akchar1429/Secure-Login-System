# Secure Login System — College Project

A Flask + SQLite demonstration of secure user registration, login, logout, and a protected dashboard.

## Features

- Password hashing with **bcrypt** (passwords are never stored as plain text).
- Parameterized SQLite queries to prevent SQL injection.
- CSRF protection for forms using Flask-WTF.
- Login and registration rate limits for a basic brute-force speed bump.
- Session cleared at login and logout; 30-minute configured session lifetime.
- HttpOnly and SameSite=Lax session cookies; Secure cookies can be enabled for HTTPS.
- Basic username, email, and password validation.
- Security response headers and generic login failure message.
- Responsive HTML/CSS user interface.

## Requirements

- Python 3.10 or newer
- pip

## Run locally (Windows PowerShell)

1. Extract the ZIP and open a terminal inside the `secure-login-system` folder.
2. Create a virtual environment:

   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

3. Install dependencies:

   ```powershell
   python -m pip install -r requirements.txt
   ```

4. Create your local environment file:

   ```powershell
   Copy-Item .env.example .env
   ```

5. Open `.env`. Replace `SECRET_KEY` with a random value generated using:

   ```powershell
   python -c "import secrets; print(secrets.token_hex(32))"
   ```

   Put the generated value after `SECRET_KEY=` in `.env`.

6. Load `.env` into your current terminal session:

   ```powershell
   Get-Content .env | Where-Object { $_ -match '^[A-Za-z_][A-Za-z0-9_]*=' -and $_ -notmatch '^\\s*#' } | ForEach-Object {
       $parts = $_ -split '=', 2
       [Environment]::SetEnvironmentVariable($parts[0], $parts[1], 'Process')
   }
   ```

7. Start the app:

   ```powershell
   python app.py
   ```

8. Open `http://127.0.0.1:5000` in your browser. Register an account, log in, visit the dashboard, and log out.

## Run locally (macOS/Linux)

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
python -c "import secrets; print(secrets.token_hex(32))"
```

Put the generated secret into `.env`, then load environment variables in the terminal:

```bash
set -a
source .env
set +a
python app.py
```

Open `http://127.0.0.1:5000`.

## Database

On first startup, `users.db` is created automatically. The `users` table stores a username, email, bcrypt password hash, and creation timestamp. The password itself is not stored.

## Important security notes

This is a **college/demo project**, not a fully audited production identity system.

- Keep `.env` private; never commit secrets to version control.
- For deployment, use HTTPS and set `COOKIE_SECURE=1`.
- The included rate limiter uses in-memory storage and is suitable only for a single-process local demo. Use a shared persistent store (such as Redis) for multi-worker deployments.
- Add email verification, password reset, monitoring, database backups, and a formal threat review before real-world use.
- Optional 2FA is not included in this starter version.
- Do not enable Flask debug mode on a public server. Deploy with a production WSGI server and a carefully configured reverse proxy.
- SQLite is suitable for a small demonstration; choose a managed database for a larger application.

## Project modules

- `app.py` — routes, database access, validation, password hashing, sessions, and security headers.
- `templates/` — login, registration, shared layout, and protected dashboard.
- `static/style.css` — responsive styling.
- `requirements.txt` — Python dependencies.
- `.env.example` — required configuration template.

## Suggested demonstration flow

1. Register with a username, email, and 12+ character password.
2. Confirm the app redirects to the login page.
3. Log in with username or email.
4. Open `/dashboard` in a private/incognito browser before logging in to demonstrate access control.
5. Log out, then try `/dashboard` again.
6. Explain that the database stores a bcrypt hash, not the original password.
7. Explain how parameterized SQL and CSRF tokens protect form requests.

## Known scope limits

The app does not currently implement two-factor authentication, email ownership verification, password reset, or a production-grade distributed rate limiter. The email validation is intentionally basic. Do not use it to store sensitive or real customer information.
