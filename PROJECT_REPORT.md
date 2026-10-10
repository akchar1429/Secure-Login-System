# SECURE LOGIN SYSTEM
## Project Report

**Project type:** Web Application / Information Security  
**Backend:** Python Flask  
**Database:** SQLite  
**Password hashing:** bcrypt

## 1. Abstract

The Secure Login System is a web application that demonstrates safer user registration and authentication. Users can create accounts, sign in with a username or email address, access a protected dashboard, and log out. The application stores bcrypt password hashes rather than plaintext passwords, uses parameterized SQL statements, validates form data, applies CSRF protection, and manages authenticated sessions.

## 2. Problem Statement

Applications that store passwords in plaintext or build SQL queries from untrusted input can expose user accounts to unauthorized access. A basic authentication application should protect stored credentials, validate incoming data, prevent common injection attacks, and restrict private pages to authenticated users.

## 3. Objectives

- Build a user registration and login workflow.
- Store password hashes using bcrypt.
- Reduce SQL injection risk with parameterized database queries.
- Validate username, email, and password fields.
- Protect form submissions with CSRF tokens.
- Add session-based authentication, protected routes, and logout.
- Provide a clear, responsive interface.

## 4. Tools and Technologies

| Component | Technology | Purpose |
|---|---|---|
| Frontend | HTML5, CSS3 | Forms and responsive interface |
| Backend | Python, Flask | Routing and authentication logic |
| Database | SQLite | User account records |
| Password security | Flask-Bcrypt | One-way password hashing |
| CSRF protection | Flask-WTF | CSRF token validation |
| Rate limiting | Flask-Limiter | Limits repeated login/register attempts |

## 5. System Modules

1. **Registration:** validates input, checks password confirmation, hashes the password, and inserts the new account.
2. **Login:** searches by username or email and compares the submitted password with the stored bcrypt hash.
3. **Session management:** clears session data at login, records the authenticated user, and clears the session on logout.
4. **Protected dashboard:** redirects unauthenticated visitors to the login page.
5. **Database layer:** uses parameterized SQLite statements and unique constraints for usernames and emails.
6. **Security controls:** CSRF protection, rate limits, cookie flags, response security headers, and generic login errors.

## 6. Database Design

**Table:** `users`

| Field | Type | Description |
|---|---|---|
| id | INTEGER | Primary key |
| username | TEXT | Unique username |
| email | TEXT | Unique email |
| password_hash | TEXT | Bcrypt hash; not the original password |
| created_at | TEXT | Account creation timestamp |

## 7. Workflow

**Registration:** User submits details → server validates inputs → password is bcrypt-hashed → parameterized INSERT stores the account → user is directed to login.

**Login:** User submits username/email and password → parameterized SELECT finds the account → bcrypt checks the password → session is cleared and regenerated in application state → authenticated user is sent to dashboard.

**Logout:** User submits the CSRF-protected logout form → session is cleared → user returns to login.

## 8. Security Measures

- **Password hashing:** bcrypt makes recovering the original password from the stored hash computationally difficult.
- **SQL injection prevention:** SQL parameters are passed separately from query text.
- **Input validation:** username format, email shape, password length, and password confirmation are checked.
- **CSRF protection:** state-changing forms include CSRF tokens.
- **Session protections:** HttpOnly and SameSite cookie attributes are configured; the session has a configured 30-minute lifetime; session data is cleared on login and logout.
- **Rate limiting:** repeated requests to login and registration routes are limited in the demo.
- **Security headers:** content type sniffing and framing are restricted, and caching is disabled for responses.

## 9. Testing Plan

| Test | Steps | Expected result |
|---|---|---|
| Valid registration | Submit valid unique details | Account is created |
| Weak password | Submit a password shorter than 12 characters | Validation error |
| Mismatched passwords | Enter different password values | Validation error |
| Duplicate account | Reuse username or email | Generic duplicate-account error |
| Valid login | Enter correct credentials | Protected dashboard opens |
| Invalid login | Enter wrong password | Generic login error |
| Protected route | Visit `/dashboard` while logged out | Redirect to login |
| Logout | Submit logout form | Session cleared; login page shown |
| SQL injection probe | Enter SQL-like text as username | Treated as ordinary data |
| CSRF check | Submit a form without a valid CSRF token | Request rejected |

## 10. Limitations and Future Enhancements

This is an educational starter project. Future work could add time-based one-time-password two-factor authentication, email verification, secure password reset, audit logging, automated tests, persistent shared rate limiting, and deployment behind HTTPS. Production deployment should include a security review, monitoring, backups, and appropriate data protection.

## 11. Conclusion

The Secure Login System demonstrates essential authentication concepts: password hashing, input validation, parameterized SQL, CSRF protection, rate limiting, session-based access control, and logout. These controls reduce common risks, but a production system requires additional engineering, operational safeguards, and security testing.
